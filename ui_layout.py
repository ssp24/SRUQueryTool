from app_functions import resource_path
from workers import DNBNumberWorker, DNBSRUThread
from styles import MAIN_STYLE, EXIT_BUTTON_STYLE
from config import CATALOGUE_URLS, METADATA_FORMATS, MAX_RESULTS
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QComboBox, QProgressBar, QSpacerItem, QSizePolicy, QShortcut, QFileDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QKeySequence, QMovie
from datetime import date
import re

# App layout:
class SRUQueryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        app = QApplication.instance()
        font = app.font()
        font.setFamily("Verdana")
        font.setPointSize(10)
        app.setFont(font)
        app.setStyleSheet("QWidget { color: black; }")

        self.setWindowTitle("SRU Query Tool")
        self.setFixedSize(750, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)  # Space between widgets
        layout.setContentsMargins(40, 40, 40, 20)  # Margins

        heading = QLabel("SRU Query Tool")
        heading.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        heading.setAlignment(Qt.AlignCenter)
        layout.addWidget(heading)

        # Create a QLabel with the text
        self.intro_label = QLabel("Mit diesem Tool können Sie die SRU-Schnittstelle der Deutschen Nationalbibliothek "
                             "abfragen und die Ergebnisse als Metadatendump herunterladen. <br> Allgemeine Informationen "
                             "zur SRU-Schnittstelle und den zur Verfügung stehenden Katalogen finden Sie unter "
                             "<a href='https://www.dnb.de/sru'>www.dnb.de/sru</a>. Weiterführende Informationen "
                             "zur Suche sowie Möglichkeiten zur Eingrenzung der Ergebnisse finden Sie unter "
                             "<a href='https://www.dnb.de/expertensuche'>www.dnb.de/expertensuche</a>.")
        self.intro_label.setWordWrap(True)  # wrap text
        self.intro_label.setOpenExternalLinks(True)  # allows the links to be clickable
        self.intro_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout.addWidget(self.intro_label)
        layout.addWidget(QLabel(" "))  # Empty label for spacing

        todo_label = QLabel("Wählen Sie einen Katalog und ein Metadatenformat aus und geben Sie Ihre Suchanfrage ein:")
        todo_label.setAlignment(Qt.AlignCenter)
        todo_label.setWordWrap(True)  # wrap text

        # Add label to layout
        layout.addWidget(todo_label)
        layout.addWidget(QLabel(" "))  # Empty label for spacing

        layout.addWidget(QLabel("Katalog:"))
        self.catalogue_combo = QComboBox()
        self.catalogue_combo.addItems(["DNB (Titeldaten)", "GND (Normdaten)", "DMA (Deutsches Musikarchiv)",
                                       "ZDB (Zeitschriftendatenbank)", "Adressdaten (ISIL- und Siegelverzeichnis)"])
        layout.addWidget(self.catalogue_combo)
        self.catalogue_combo.currentIndexChanged.connect(self.update_metadata_formats)

        layout.addWidget(QLabel("Metadatenformat:"))
        self.metadata_combo = QComboBox()
        layout.addWidget(self.metadata_combo)

        layout.addWidget(QLabel(" "))
        layout.addWidget(QLabel("Ihre Suchanfrage ('search query'):"))
        self.query_input = QLineEdit()
        layout.addWidget(self.query_input)
        self.query_input.textChanged.connect(self.disable_download_button)  # Track changes in entered text

        self.output_label = QLabel("")
        self.output_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.output_label)

        # Button layout
        button_layout = QHBoxLayout()

        # Check search query button
        self.check_button = QPushButton("Suchanfrage prüfen")
        self.check_button.clicked.connect(self.check_search_query)
        self.check_button.setFixedSize(180, 40)
        self.return_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.return_shortcut.activated.connect(self.check_search_query)

        # Download XML button
        self.download_button = QPushButton("Download XML")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.get_xml)
        self.download_button.setFixedSize(180, 40)
        layout.addWidget(self.download_button)

        # center button
        button_layout.addStretch()
        button_layout.addWidget(self.check_button)
        button_layout.addSpacing(10)  # Abstand zwischen den Buttons
        button_layout.addWidget(self.download_button)
        button_layout.addStretch()

        # Add button layout to main style
        layout.addLayout(button_layout)

        # Results label:
        self.results_label = QLabel(" ")
        self.results_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.results_label)

        # WARNING label
        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)
        self.warning_label.setWordWrap(True)
        self.warning_label.setTextFormat(Qt.RichText)
        self.warning_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Progress Bar:
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Spinner-Animation
        self.spinner_label = QLabel(self)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner = QMovie(resource_path("images/spinner.gif"))
        self.spinner.setScaledSize(QSize(40, 40))  # optional: Spinnergröße anpassen
        self.spinner_label.setMovie(self.spinner)
        self.spinner_label.setVisible(False)
        layout.addWidget(self.spinner_label)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Cancel Button
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setVisible(False)
        self.cancel_button.setFixedSize(180, 40)
        self.cancel_button.clicked.connect(self.stop_download)
        cancel_layout.addWidget(self.cancel_button)
        cancel_layout.addStretch()
        layout.addLayout(cancel_layout)

        # Adding spacer to push the exit button to the bottom
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Right-align exit button
        exit_layout = QHBoxLayout()
        exit_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.exit_button = QPushButton("Schließen")
        self.exit_button.setFixedSize(180, 40)
        self.exit_button.clicked.connect(self.close)
        exit_layout.addWidget(self.exit_button)

        # Add logo:
        self.logo_label = QLabel(self)
        pixmap = QPixmap(resource_path("images/logo.gif"))
        self.logo_label.setPixmap(pixmap.scaled(90, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.logo_label.setGeometry(self.width() - 110, 10, 90, 60)
        self.logo_label.raise_()

        layout.addLayout(exit_layout)

        self.update_metadata_formats()
        self.apply_styles()

    def update_metadata_formats(self):
        self.metadata_combo.clear()
        selected_catalogue = self.catalogue_combo.currentText()
        formats = METADATA_FORMATS.get(selected_catalogue, [])
        self.metadata_combo.addItems(formats)

    def check_search_query(self):
        self.status_label.setText("")
        self.warning_label.setVisible(False)
        self.results_label.setText("")
        try:
            catalogue = self.catalogue_combo.currentText()
            metadata = self.metadata_combo.currentText()
            query = self.query_input.text()

            # set cat_url (looking up mapping in config.py)
            cat_url = CATALOGUE_URLS.get(catalogue)

            if cat_url and metadata and query:
                # Show spinner
                self.spinner_label.setVisible(True)
                self.spinner.start()
                self.check_button.setEnabled(False)

                # Start Worker-Thread
                self.worker = DNBNumberWorker(query, metadata, cat_url)
                self.worker.finished.connect(self.handle_dnb_number_result)
                self.worker.start()

        except Exception as e:
            self.results_label.setText(f"Ein Fehler ist aufgetreten: {str(e)}")
            print(f"Error: {str(e)}")

    def handle_dnb_number_result(self, result):
        # Hide spinner:
        self.spinner.stop()
        self.spinner_label.setVisible(False)
        self.check_button.setEnabled(True)

        try:
            if isinstance(result, int):
                if result == 0:
                    display_text = f"Ihre Suchanfrage ergab keine Treffer. Bitte geben Sie eine neue Anfrage ein."
                    self.results_label.setText(display_text)
                    self.download_button.setEnabled(False)
                elif 0 < result <= 100000:
                    display_text = f"Ihre Suchanfrage ergibt {result} Treffer."
                    self.results_label.setText(display_text)
                    self.warning_label.setVisible(False)
                    self.download_button.setEnabled(True)
                elif result > MAX_RESULTS:
                    display_text = f"Ihre Suchanfrage ergibt {result} Treffer."
                    self.results_label.setText(display_text)
                    self.warning_label.setText(
                        "<div align='center'><br>Warnung!<br><br> Ihre Anfrage ergibt mehr als 100.000 Treffer! "
                        "Bitte teilen Sie Ihre Anfrage so auf, dass diese "
                        "maximal 100.000 Treffer ergeben (z. B. mit Zeitabschnitten).</div>"
                    )
                    self.warning_label.setVisible(True)
                    self.warning_label.setWordWrap(True)
                    self.download_button.setEnabled(False)
            elif isinstance(result, str) and result.startswith("FEHLER"):
                self.warning_label.setText(result)
                self.warning_label.setVisible(True)
                self.download_button.setEnabled(False)
            else:
                raise ValueError("Unerwarteter Rückgabewert")
        except Exception as e:
            self.warning_label.setText(f"<div align='center'>Ein unbekannter Fehler ist aufgetreten:<br>{str(e)}</div>")
            self.warning_label.setVisible(True)
            self.download_button.setEnabled(False)


    def get_xml(self):
        catalogue = self.catalogue_combo.currentText()
        metadata = self.metadata_combo.currentText()
        query = self.query_input.text()
        self.download_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText("Downloading...")

        # set cat_url (from mapping in config.py)
        cat_url = CATALOGUE_URLS.get(catalogue)

        if cat_url and metadata and query:
            today = str(date.today())
            today = today.replace("-", "")
            name = query.replace(" ", "_")
            name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name).strip('. ')
            filename = today + "_" + metadata + "_" + name[:50]

            # Define path and filename:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Datei speichern unter",
                filename,  # Default-Name
            )
            if not save_path:
                # User hat Abbrechen gedrückt
                self.download_button.setEnabled(True)
                self.cancel_button.setVisible(False)
                self.progress_bar.setVisible(False)
                self.status_label.setText("Download abgebrochen.")
                return  # NICHT fortfahren!

            self.dnb_sru_thread = DNBSRUThread(query, metadata, cat_url, save_path)
            self.dnb_sru_thread.progress_signal.connect(self.update_progress)
            self.dnb_sru_thread.result_signal.connect(self.handle_result)
            self.dnb_sru_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_result(self, success):
        if success:
            self.status_label.setText("Download erfolgreich!")
        else:
            self.status_label.setText("Download fehlgeschlagen.")

        self.progress_bar.setVisible(False)
        self.download_button.setEnabled(True)
        self.cancel_button.setVisible(False)

    def stop_download(self):
        if hasattr(self, "dnb_sru_thread") and self.dnb_sru_thread.isRunning():
            self.dnb_sru_thread.stop()
            self.dnb_sru_thread.quit()
            self.dnb_sru_thread.wait()

        # Clear UI
        self.status_label.setText("Download abgebrochen!")
        self.status_label.setVisible(True)
        self.progress_bar.setVisible(False)
        self.cancel_button.setVisible(False)
        self.download_button.setEnabled(True)

    def disable_download_button(self):
        self.download_button.setEnabled(False)
        self.results_label.setText(" ")  #Opt: Clear results label
        self.warning_label.setVisible(False)  #Show no warning

    def apply_styles(self):
        #Main Style:
        self.setStyleSheet(MAIN_STYLE)
        # Exit-Button:
        self.exit_button.setStyleSheet(EXIT_BUTTON_STYLE)
