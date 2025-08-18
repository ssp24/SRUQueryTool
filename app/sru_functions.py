import requests
from bs4 import BeautifulSoup as soup
from time import sleep
import certifi

# SRU-Funktionen
def dnb_sru_number(query, metadata, base_url):
    params = {'recordSchema': metadata,
              'operation': 'searchRetrieve',
              'version': '1.1',
              'query': query
              }

    if metadata != "mods-xml":
        params.update({'maximumRecords': '100'})
    try:
        r1 = requests.get(base_url, params=params, verify=certifi.where())
        r1.raise_for_status()  # Raise an exception for bad status codes
        xml1 = soup(r1.content, features="xml")

        # Check for diagnostics:
        treffer = xml1.find("numberOfRecords")
        diag = xml1.find("diag:diagnostic")
        if treffer and treffer.text.isdigit():
            return int(treffer.text)
        elif diag:
            msg = diag.find("diag:details")
            errormsg = f"FEHLER: {msg.text}"
            return errormsg
        else:
            return 0
    except Exception as e:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(f"Fehler bei SRU-Abfrage:\n{str(e)}\n")
        return f"FEHLER: {str(e)}"



def dnb_sru(query, metadata, base_url, progress_signal, filename, is_running):
    #session = requests.Session()

    params = {'recordSchema': metadata,
              'operation': 'searchRetrieve',
              'version': '1.1',
              'query': query
              }

    if metadata != "mods-xml":
        params.update({'maximumRecords': '100'})

    r = requests.get(base_url, params=params, verify=certifi.where())
    xml = soup(r.content, features="xml")
    diagnostics = xml.find_all('diagnostics')
    if diagnostics:
        error = "error"
        return error
    else:
        if metadata == "oai_dc":
            records = xml.find_all('record')
        elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/dnb":
            records = xml.find_all('record', {'type': 'Bibliographic'})
        elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/zdb":
            records = xml.find_all('record', {'type': 'Bibliographic'})
        elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/authorities":
            records = xml.find_all('record', {'type': 'Authority'})
        elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/dnb.dma":
            records = xml.find_all('record', {'type': 'Bibliographic'})
        else:
            records = xml.find_all('record')

        treffer = xml.find_all("numberOfRecords")[0].text
        treffer = int(treffer)
        if treffer > 100:
            loops = int(treffer / 100) + 1
        else:
            loops = 1
        print("Records found: ", treffer)
        print("Anzahl notwendiger Abfragen: ", loops)

        if treffer == 0:
            print("No results found.")
            progress_signal.emit(100)
        elif metadata != "mods-xml" and 1 <= treffer <= 100:
            with open(f"{filename}.xml", 'w', encoding="utf-8") as f:
                f.write(str(xml))
                progress_signal.emit(100)
                return True
        elif metadata == "mods-xml" and 1 <= treffer <= 10:
            with open(f"{filename}.xml", 'w', encoding="utf-8") as f:
                f.write(str(xml))
                progress_signal.emit(100)
                return True
        elif metadata != "mods-xml" and treffer > 100:
            progress_increment = 100 / loops

            # Define XML-header and footer:
            header_marc = f'''<?xml version="1.0" encoding="utf-8"?><searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/"> 
                <version>1.1</version><numberOfRecords>{str(treffer)}</numberOfRecords>
                <records><record><recordSchema>MARC21-xml</recordSchema><recordPacking>xml</recordPacking><recordData>'''
            header_dc = f'''<searchRetrieveResponse><version>1.1</version><numberOfRecords>{str(treffer)}</numberOfRecords><records>'''
            header_pica = f'''<?xml version="1.0" encoding="utf-8"?><searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/"><version>1.1</version>
                <numberOfRecords>{str(treffer)}</numberOfRecords><records>'''
            footer_marc = f'''</recordData></record></records><echoedSearchRetrieveRequest><version>1.1</version>
                <query>{query}</query><xQuery xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
                <recordSchema>MARC21-xml</recordSchema></echoedSearchRetrieveRequest>
                </searchRetrieveResponse>'''
            footer_dc = f'''</records><echoedSearchRetrieveRequest><version>1.1</version><query>{query}</query>
                <recordSchema>oai_dc</recordSchema></echoedSearchRetrieveRequest></searchRetrieveResponse>'''
            footer_rdf = f'''</records><echoedSearchRetrieveRequest><version>1.1</version><query>{query}</query>
                <recordSchema>RDFxml</recordSchema></echoedSearchRetrieveRequest></searchRetrieveResponse>'''
            footer_pica = f'''</records><echoedSearchRetrieveRequest><version>1.1</version><query>{query}</query>
                <xQuery xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/><maximumRecords>100</maximumRecords><recordSchema>PicaPlus-xml</recordSchema>
                </echoedSearchRetrieveRequest></searchRetrieveResponse>'''

            if metadata == "oai_dc":
                header = header_dc
            elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/dnb":
                header = header_marc
            elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/zdb":
                header = header_marc
            elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/authorities":
                header = header_marc
            elif metadata == "RDFxml":
                header = header_dc
            elif metadata == "PicaPlus-xml":
                header = header_pica
            else:
                header = " "

            # Open file and write header and first records:
            with open(f"{filename}.xml", 'w', encoding="utf-8") as f:
                f.write(header)
                for record in records:
                    f.write(str(record))

            print("successfully written header and first records")

            num_results = 100
            i = 101
            count = 0
            progress_percent = progress_increment  # Start with progress after first request

            while num_results == 100:
                if not is_running():
                    # Download abgebrochen
                    progress_signal.emit(0)
                    return

                params.update({'startRecord': i})
                r = requests.get(base_url, params=params)
                xml = soup(r.content, features="xml")
                if metadata == "oai_dc":
                    new_records = xml.find_all('record')
                elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/dnb":
                    new_records = xml.find_all('record', {'type': 'Bibliographic'})
                elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/zdb":
                    new_records = xml.find_all('record', {'type': 'Bibliographic'})
                elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/authorities":
                    new_records = xml.find_all('record', {'type': 'Authority'})
                elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/dnb.dma":
                    new_records = xml.find_all('record', {'type': 'Bibliographic'})
                else:
                    new_records = xml.find_all('record')
                records += new_records
                i += 100
                count += 1
                num_results = len(new_records)
                progress_percent += progress_increment
                progress_signal.emit(int(min(progress_percent, 100)))

                # Add records:
                with open(f"{filename}.xml", 'a', encoding="utf-8") as f:
                    for record in new_records:
                        f.write(str(record))

                if num_results < 100:
                    if metadata == "oai_dc":
                        footer = footer_dc
                    elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/dnb":
                        footer = footer_marc
                    elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/zdb":
                        footer = footer_marc
                    elif metadata == "MARC21-xml" and base_url == "https://services.dnb.de/sru/authorities":
                        footer = footer_marc
                    elif metadata == "RDFxml":
                        footer = footer_rdf
                    elif metadata == "PicaPlus-xml":
                        footer = footer_pica
                    else:
                        footer = ""

                    with open(f"{filename}.xml", 'a', encoding="utf-8") as f:
                        f.write(footer)

                    print("successfully written all records and footer.")
                    progress_signal.emit(100)
                    return True

                if count % 50 == 0:
                    if not is_running():
                        # Download abgebrochen
                        progress_signal.emit(0)
                        return
                    print("sleeping...")
                    sleep(3)
                else:
                    continue


        # Sonderlocke für mods...
        elif metadata == "mods-xml" and treffer > 10:
            loops = int(treffer / 10) + 1
            progress_increment = 100 / loops

            # Define XML-header and footer:
            header_mods = f'''<?xml version="1.0" encoding="utf-8"?>
                                <searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/">
                                    <version>1.1</version>
                                    <numberOfRecords>{str(treffer)}</numberOfRecords>
                                        <records>'''
            footer_mods = f'''</records><echoedSearchRetrieveRequest><version>1.1</version><query>{query}</query>
                                <xQuery xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/><recordSchema>mods-xml</recordSchema>
                                </echoedSearchRetrieveRequest></searchRetrieveResponse>'''

            num_results = 10
            i = 11
            progress_percent = progress_increment  # Start with progress after first request

            count = 0

            while num_results == 10:
                if not is_running():
                    # Download abgebrochen
                    progress_signal.emit(0)
                    return

                params.update({'startRecord': i})
                r = requests.get(base_url, params=params)
                xml = soup(r.content, features="xml")
                new_records = xml.find_all('record')
                records += new_records
                i += 10
                count += 1
                num_results = len(new_records)
                progress_percent += progress_increment
                progress_signal.emit(int(min(progress_percent, 100)))

                if count % 50 == 0:
                    print("sleeping...")
                    sleep(3)
                else:
                    continue

            recordlist = ""
            for record in records:
                recordlist += str(record)

            xmlplus = header_mods + recordlist + footer_mods

            with open(f"{filename}.xml", 'w', encoding='utf-8') as f1:
                f1.write(xmlplus)

            return True

        else:
            print("Something went wrong.")