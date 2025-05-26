from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QPushButton, QLabel, QScrollArea, QFrame, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class TasksWindow(QWidget):
    """Окно заданий с вкладками по темам"""

    task_selected = pyqtSignal(str, str, str)  # тема, задание, описание

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_tasks()

    def init_ui(self):
        """Создание интерфейса"""
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Задания по программированию")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        layout.addWidget(title)

        # Создаем вкладки для тем
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin: 2px;
                border-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        layout.addWidget(self.tab_widget)

        # Кнопка возврата в меню
        back_btn = QPushButton("← Вернуться в меню")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_btn.clicked.connect(self.main_window.show_menu)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def load_tasks(self):
        """Загрузка заданий по темам"""
        # Определяем темы и задания
        self.tasks_data = {
            "Цикл с условием": [
                {
                    "name": "Наибольший общий делитель",
                    "description": "Найти наибольший общий делитель (НОД) двух натуральных чисел, используя алгоритм Евклида.",
                    "example": "НОД(48, 18) = 6",
                    "template": "# Алгоритм Евклида\na = int(input('Введите первое число: '))\nb = int(input('Введите второе число: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Цифры числа",
                    "description": "Разложить натуральное число на отдельные цифры и вывести их в обратном порядке.",
                    "example": "1234 → 4, 3, 2, 1",
                    "template": "# Разбиение числа на цифры\nn = int(input('Введите число: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Простые множители",
                    "description": "Разложить натуральное число на простые сомножители и вывести их.",
                    "example": "60 = 2 × 2 × 3 × 5",
                    "template": "# Разложение на простые множители\nn = int(input('Введите число: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Сумма цифр числа",
                    "description": "Найти сумму всех цифр натурального числа до получения однозначного числа.",
                    "example": "1234 → 1+2+3+4 = 10 → 1+0 = 1",
                    "template": "# Сумма цифр числа\nn = int(input('Введите число: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Число-палиндром",
                    "description": "Проверить, является ли натуральное число палиндромом.",
                    "example": "12321 - палиндром, 1234 - не палиндром",
                    "template": "# Проверка на палиндром\nn = int(input('Введите число: '))\n\n# Ваш код здесь\n"
                }
            ],
            "Цикл с переменной": [
                {
                    "name": "Простое число",
                    "description": "Проверить, является ли введенное натуральное число простым.",
                    "example": "17 - простое, 15 - составное",
                    "template": "# Проверка на простоту\nn = int(input('Введите число: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Таблица умножения",
                    "description": "Вывести таблицу умножения для числа от 1 до 10.",
                    "example": "5 × 1 = 5, 5 × 2 = 10, ...",
                    "template": "# Таблица умножения\nn = int(input('Введите число: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Факториал",
                    "description": "Вычислить факториал натурального числа n.",
                    "example": "5! = 1 × 2 × 3 × 4 × 5 = 120",
                    "template": "# Факториал числа\nn = int(input('Введите число: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Последовательность Фибоначчи",
                    "description": "Вывести первые n чисел последовательности Фибоначчи.",
                    "example": "1, 1, 2, 3, 5, 8, 13, 21...",
                    "template": "# Числа Фибоначчи\nn = int(input('Количество чисел: '))\n\n# Ваш код здесь\n"
                },
                {
                    "name": "Совершенное число",
                    "description": "Найти все совершенные числа до заданного предела.",
                    "example": "6 = 1 + 2 + 3 (совершенное число)",
                    "template": "# Совершенные числа\nlimit = int(input('Введите предел: '))\n\n# Ваш код здесь\n"
                }
            ]
        }

        # Создаем вкладки для каждой темы
        for theme_name, tasks in self.tasks_data.items():
            self.create_theme_tab(theme_name, tasks)

    def create_theme_tab(self, theme_name: str, tasks: list):
        """Создание вкладки для темы"""
        tab_widget = QWidget()
        layout = QVBoxLayout()

        # Прогресс-бар для темы
        progress_label = QLabel(f"Прогресс по теме: 0/{len(tasks)}")
        progress_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(progress_label)

        progress_bar = QProgressBar()
        progress_bar.setMaximum(len(tasks))
        progress_bar.setValue(0)
        layout.addWidget(progress_bar)

        # Скроллируемая область для заданий
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Создаем карточки заданий
        for i, task in enumerate(tasks):
            task_btn = QPushButton(task['name'])
            task_btn.setCheckable(True)
            task_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px;
                    font-size: 14px;
                    border-radius: 5px;
                    margin: 5px;
                    text-align: left;
                }
                QPushButton:checked {
                    background-color: #2980b9;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)

            # ИСПРАВЛЕНИЕ: Правильное создание обработчика
            def create_handler(theme_name, task_data, button):
                def handler():
                    # Снимаем выделение с других кнопок в этой теме
                    for j in range(scroll_layout.count()):
                        widget = scroll_layout.itemAt(j).widget()
                        if widget and widget != button:
                            widget.setChecked(False)

                    # Устанавливаем выделение на текущую кнопку
                    button.setChecked(True)

                    # Отправляем сигнал выбора задания
                    self.task_selected.emit(theme_name, task_data['name'], task_data['description'])

                return handler

            # Подключаем обработчик
            task_btn.clicked.connect(create_handler(theme_name, task, task_btn))
            scroll_layout.addWidget(task_btn)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        tab_widget.setLayout(layout)
        self.tab_widget.addTab(tab_widget, theme_name)

