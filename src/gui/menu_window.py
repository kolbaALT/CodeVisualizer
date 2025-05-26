from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MenuWindow(QWidget):
    """Окно главного меню приложения"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        """Создание интерфейса меню"""
        # Основной вертикальный layout
        layout = QVBoxLayout()
        layout.setSpacing(30)  # Расстояние между элементами

        # Добавляем отступ сверху
        layout.addItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum,
                                   QSizePolicy.Policy.Expanding))

        # Заголовок приложения
        title = QLabel("CodeVisualizer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # Подзаголовок
        subtitle = QLabel("Визуализатор выполнения кода")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 40px;")
        layout.addWidget(subtitle)

        # Контейнер для кнопок
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        # Создаем кнопки
        self.create_menu_buttons(button_layout)

        # Центрируем кнопки
        button_container = QHBoxLayout()
        button_container.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding,
                                             QSizePolicy.Policy.Minimum))
        button_container.addLayout(button_layout)
        button_container.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding,
                                             QSizePolicy.Policy.Minimum))

        layout.addLayout(button_container)

        # Добавляем отступ снизу
        layout.addItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum,
                                   QSizePolicy.Policy.Expanding))

        self.setLayout(layout)

        # Стили для всего окна
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
            }
        """)

    def create_menu_buttons(self, layout):
        """Создание кнопок меню"""
        # Стиль для кнопок
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """

        # Кнопка "Визуализатор"
        visualizer_btn = QPushButton("🔍 Визуализатор")
        visualizer_btn.setStyleSheet(button_style)
        visualizer_btn.clicked.connect(self.open_visualizer)
        layout.addWidget(visualizer_btn)

        # Кнопка "Задания"
        tasks_btn = QPushButton("📝 Задания")
        tasks_btn.setStyleSheet(
            button_style.replace("#3498db", "#95a5a6").replace("#2980b9", "#7f8c8d").replace("#21618c", "#6c7b7d"))
        tasks_btn.clicked.connect(self.open_tasks)
        layout.addWidget(tasks_btn)

        # Кнопка "Настройки"
        settings_btn = QPushButton("⚙️ Настройки")
        settings_btn.setStyleSheet(
            button_style.replace("#3498db", "#95a5a6").replace("#2980b9", "#7f8c8d").replace("#21618c", "#6c7b7d"))
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        # Кнопка "Выход"
        exit_btn = QPushButton("❌ Выход")
        exit_btn.setStyleSheet(
            button_style.replace("#3498db", "#e74c3c").replace("#2980b9", "#c0392b").replace("#21618c", "#a93226"))
        exit_btn.clicked.connect(self.exit_app)
        layout.addWidget(exit_btn)

    def open_visualizer(self):
        """Открыть визуализатор"""
        self.main_window.show_visualizer()

    def open_tasks(self):
        """Открыть задания"""
        self.main_window.show_tasks()

    def open_settings(self):
        """Открыть настройки"""
        self.show_settings_dialog()

    def show_settings_dialog(self):
        """Показать диалог настроек"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox

        # Создаем диалог настроек
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки")
        dialog.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Настройки приложения")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # Стиль для кнопок настроек
        settings_button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """

        # Кнопки переключения темы
        theme_label = QLabel("Тема оформления:")
        theme_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(theme_label)

        theme_layout = QHBoxLayout()

        light_theme_btn = QPushButton("☀️ Светлая тема")
        light_theme_btn.setStyleSheet(settings_button_style)
        light_theme_btn.clicked.connect(lambda: self.apply_theme('light'))
        theme_layout.addWidget(light_theme_btn)

        dark_theme_btn = QPushButton("🌙 Темная тема")
        dark_theme_btn.setStyleSheet(settings_button_style.replace("#3498db", "#34495e"))
        dark_theme_btn.clicked.connect(lambda: self.apply_theme('dark'))
        theme_layout.addWidget(dark_theme_btn)

        layout.addLayout(theme_layout)

        # Кнопка горячих клавиш
        hotkeys_btn = QPushButton("⌨️ Горячие клавиши")
        hotkeys_btn.setStyleSheet(settings_button_style.replace("#3498db", "#27ae60"))
        hotkeys_btn.clicked.connect(self.show_hotkeys)
        layout.addWidget(hotkeys_btn)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet(settings_button_style.replace("#3498db", "#95a5a6"))
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def apply_theme(self, theme: str):
        """Применение темы"""
        if theme == 'dark':
            # Темная тема
            self.setStyleSheet("""
                QWidget {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QLabel {
                    color: #ecf0f1;
                }
                QPushButton {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: none;
                    padding: 15px 30px;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 8px;
                    min-width: 200px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
            """)
            # Применяем тему к главному окну
            self.main_window.setStyleSheet("""
                QMainWindow {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
            """)
        else:
            # Светлая тема (по умолчанию)
            self.setStyleSheet("""
                QWidget {
                    background-color: #ecf0f1;
                }
            """)
            self.main_window.setStyleSheet("")

        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Тема изменена", f"Применена {'темная' if theme == 'dark' else 'светлая'} тема!")

    def show_hotkeys(self):
        """Показ горячих клавиш"""
        from PyQt6.QtWidgets import QMessageBox
        hotkeys_text = """
    <b>Горячие клавиши:</b><br><br>

    <b>Выполнение кода:</b><br>
    • F5 - Запустить код<br>
    • F6 - Шаг вперед<br>
    • F7 - Шаг назад<br>
    • F8 - Сбросить выполнение<br><br>

    <b>Работа с файлами:</b><br>
    • Ctrl+N - Новый файл<br>
    • Ctrl+O - Открыть файл<br>
    • Ctrl+S - Сохранить файл<br>
    • Ctrl+Q - Выход<br><br>

    <b>Навигация:</b><br>
    • Esc - Вернуться в меню<br>
    • Enter - Запустить выделенное<br>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("Горячие клавиши")
        msg.setText(hotkeys_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def exit_app(self):
        """Выход из приложения"""
        self.main_window.close()
