from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from .menu_window import MenuWindow
from .visualizer_window import VisualizerWindow


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Настройки окна
        self.setWindowTitle("CodeVisualizer - Визуализатор кода")
        self.setGeometry(100, 100, 1200, 800)  # x, y, ширина, высота

        # Создаем стековый виджет для переключения между экранами
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создаем и добавляем экран меню
        self.menu_window = MenuWindow(self)
        self.stacked_widget.addWidget(self.menu_window)
        # Создаем и добавляем экран визуализатора
        self.visualizer_window = VisualizerWindow(self)
        self.stacked_widget.addWidget(self.visualizer_window)

        # Показываем меню по умолчанию
        self.show_menu()

    def show_menu(self):
        """Показать главное меню"""
        self.stacked_widget.setCurrentWidget(self.menu_window)

    def show_visualizer(self):
        """Показать визуализатор"""
        try:
            from .visualizer_window import VisualizerWindow
            if not hasattr(self, 'visualizer_window'):
                self.visualizer_window = VisualizerWindow(self)
                self.stacked_widget.addWidget(self.visualizer_window)
            self.stacked_widget.setCurrentWidget(self.visualizer_window)
        except Exception as e:
            print(f"ERROR при открытии визуализатора: {e}")

    def show_tasks(self):
        """Показать окно заданий"""
        from .tasks_window import TasksWindow

        # Создаем окно заданий если его еще нет
        if not hasattr(self, 'tasks_window'):
            self.tasks_window = TasksWindow(self)
            # Подключаем сигнал выбора задания
            self.tasks_window.task_selected.connect(self.open_task_in_visualizer)

        # Скрываем меню и показываем задания
        self.menu_window.hide()
        self.tasks_window.show()
        self.setCentralWidget(self.tasks_window)

    def open_task_in_visualizer(self, theme: str, task_name: str, description: str):
        """Открыть задание в визуализаторе"""
        # Переходим к визуализатору
        self.show_visualizer()

        # Устанавливаем описание задания
        self.visualizer_window.set_task_description(theme, task_name, description)

        # Загружаем шаблон кода для задания
        self.load_task_template(theme, task_name)

    def load_task_template(self, theme: str, task_name: str):
        """Загрузка шаблона кода для задания"""
        # Получаем шаблон из данных заданий
        if hasattr(self, 'tasks_window'):
            for theme_data in self.tasks_window.tasks_data.get(theme, []):
                if theme_data['name'] == task_name:
                    template = theme_data.get('template', '# Напишите ваш код здесь\n')
                    self.visualizer_window.code_editor.setText(template)
                    break

    def show_tasks(self):
        """Показать окно заданий"""
        from .tasks_window import TasksWindow
        self.tasks_window = TasksWindow(self)

        # ДОБАВЬ ЭТУ СТРОКУ:
        self.tasks_window.task_selected.connect(self.on_task_selected)

        self.stacked_widget.addWidget(self.tasks_window)
        self.stacked_widget.setCurrentWidget(self.tasks_window)

    def on_task_selected(self, theme: str, task_name: str, description: str):
        """Обработчик выбора задания"""
        print(f"DEBUG: Выбрана задача - {theme}: {task_name}")

        # Создаем или получаем окно визуализатора
        if not hasattr(self, 'visualizer_window'):
            from .visualizer_window import VisualizerWindow
            self.visualizer_window = VisualizerWindow(self)
            self.stacked_widget.addWidget(self.visualizer_window)

        # Устанавливаем описание задачи
        self.visualizer_window.set_task_description(theme, task_name, description)

        # Переключаемся на визуализатор
        self.stacked_widget.setCurrentWidget(self.visualizer_window)

    def create_header(self, layout):
        """Создание заголовка"""
        header_layout = QHBoxLayout()

        # Заголовок
        title = QLabel("CodeVisualizer")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px 0;")
        header_layout.addWidget(title)

        # Растягиваем пространство
        header_layout.addStretch()

        # Кнопка сброса всего прогресса
        reset_all_btn = QPushButton("🔄 Сбросить весь прогресс")
        reset_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        reset_all_btn.clicked.connect(self.reset_all_progress)
        header_layout.addWidget(reset_all_btn)

        layout.addLayout(header_layout)

    def reset_all_progress(self):
        """Сброс всего прогресса"""
        from ..data.progress_manager import progress_manager
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            'Сброс прогресса',
            'Вы уверены, что хотите сбросить весь прогресс по всем темам?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            progress_manager.reset_progress()
            # Обновляем интерфейс, если находимся в окне заданий
            if hasattr(self, 'tasks_window') and self.tasks_window:
                self.tasks_window.refresh_ui()
            QMessageBox.information(self, "Прогресс сброшен", "Весь прогресс успешно сброшен!")
