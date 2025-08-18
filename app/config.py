# URLs zu den verschiedenen SRU-Katalogen
CATALOGUE_URLS = {
    "DNB (Titeldaten)": "https://services.dnb.de/sru/dnb",
    "DMA (Deutsches Musikarchiv)": "https://services.dnb.de/sru/dnb.dma",
    "GND (Normdaten)": "https://services.dnb.de/sru/authorities",
    "ZDB (Zeitschriftendatenbank)": "https://services.dnb.de/sru/zdb",
    "Adressdaten (ISIL- und Siegelverzeichnis)": "https://services.dnb.de/sru/bib"
}

# Metadatenformate pro Katalog
METADATA_FORMATS = {
    "DNB (Titeldaten)": ["MARC21-xml", "oai_dc", "RDFxml", "mods-xml"],
    "GND (Normdaten)": ["MARC21-xml", "RDFxml"],
    "DMA (Deutsches Musikarchiv)": ["MARC21-xml", "oai_dc", "RDFxml", "mods-xml"],
    "ZDB (Zeitschriftendatenbank)": ["MARC21-xml", "MARC21plus-1-xml", "oai_dc", "RDFxml"],
    "Adressdaten (ISIL- und Siegelverzeichnis)": ["RDFxml", "PicaPlus-xml"]
}

# Grenzwert für Warnungen
MAX_RESULTS = 100000