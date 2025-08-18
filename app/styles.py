MAIN_STYLE = """
            QWidget {
                background-color: #f0f0f0;
                font-size: 14px;
            }
            QLabel {
                color: #333;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QProgressBar {
                border: 2px solid #007BFF;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #007BFF;
            }

        """

EXIT_BUTTON_STYLE = """
                QPushButton {
                    background-color: #FF0000;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #FF5733;
                }
            """