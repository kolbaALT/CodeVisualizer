from PyQt6.QtWidgets import QMainWindow, QStackedWidget
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
        self.stacked_widget.setCurrentWidget(self.visualizer_window)

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

