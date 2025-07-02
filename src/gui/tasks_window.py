from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QTabWidget, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json
import os


class MockProgressManager:
    """Заглушка для progress_manager на случай ошибок загрузки"""

    def get_theme_progress(self, theme, total_tasks):
        return 0, total_tasks

    def is_task_completed(self, theme, task_name):
        return False

    def reset_theme_progress(self, theme):
        pass

    def mark_task_completed(self, theme, task_name):
        pass


class TasksWindow(QWidget):
    """Окно с заданиями по программированию"""

    task_selected = pyqtSignal(str, str, str)  # theme, task_name, description

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.progress_manager = None

        print("DEBUG: Инициализация TasksWindow")

        # Загружаем данные задач
        self.load_tasks_data()

        # Проверяем, что данные загружены
        if not self.tasks_data:
            print("CRITICAL: Данные задач не загружены!")
        else:
            print(f"SUCCESS: Загружено {len(self.tasks_data)} тем")

        # Инициализируем UI
        self.init_ui()

        # Загружаем progress_manager после инициализации UI
        self.load_progress_manager()

    def load_progress_manager(self):
        """Безопасная загрузка progress_manager"""
        try:
            from ..data.progress_manager import progress_manager
            self.progress_manager = progress_manager
            print("DEBUG: Progress manager загружен успешно")
        except Exception as e:
            print(f"WARNING: Не удалось загрузить progress_manager: {e}")
            # Создаем заглушку
            self.progress_manager = MockProgressManager()

    def load_tasks_data(self):
        """Загрузка данных задач"""
        try:
            # Полные данные задач
            self.tasks_data = {
                "Цикл с условием": {
                    "Наибольший общий делитель": {
                        "name": "Наибольший общий делитель",
                        "description": "Найти наибольший общий делитель (НОД) двух натуральных чисел, используя алгоритм Евклида.",
                        "difficulty": "medium"
                    },
                    "Цифры числа": {
                        "name": "Цифры числа",
                        "description": "Разложить натуральное число на отдельные цифры и вывести их в обратном порядке.",
                        "difficulty": "easy"
                    },
                    "Простые множители": {
                        "name": "Простые множители",
                        "description": "Разложить натуральное число на простые сомножители и вывести их.",
                        "difficulty": "medium"
                    },
                    "Сумма цифр числа": {
                        "name": "Сумма цифр числа",
                        "description": "Найти сумму всех цифр натурального числа до получения однозначного числа.",
                        "difficulty": "easy"
                    },
                    "Число-палиндром": {
                        "name": "Число-палиндром",
                        "description": "Проверить, является ли натуральное число палиндромом.",
                        "difficulty": "easy"
                    }
                },
                "Цикл с переменной": {
                    "Простое число": {
                        "name": "Простое число",
                        "description": "Проверить, является ли введенное натуральное число простым.",
                        "difficulty": "medium"
                    },
                    "Таблица умножения": {
                        "name": "Таблица умножения",
                        "description": "Вывести таблицу умножения для числа от 1 до 10.",
                        "difficulty": "easy"
                    },
                    "Факториал": {
                        "name": "Факториал",
                        "description": "Вычислить факториал натурального числа n.",
                        "difficulty": "easy"
                    },
                    "Последовательность Фибоначчи": {
                        "name": "Последовательность Фибоначчи",
                        "description": "Вывести первые n чисел последовательности Фибоначчи.",
                        "difficulty": "medium"
                    },
                    "Совершенное число": {
                        "name": "Совершенное число",
                        "description": "Найти все совершенные числа до заданного предела.",
                        "difficulty": "hard"
                    }
                }
            }
            print("DEBUG: Данные задач загружены успешно")
            print(f"DEBUG: Количество тем: {len(self.tasks_data)}")
            for theme, tasks in self.tasks_data.items():
                print(f"DEBUG: Тема '{theme}': {len(tasks)} задач")
        except Exception as e:
            print(f"ERROR: Ошибка загрузки данных задач: {e}")
            self.tasks_data = {}

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной вертикальный layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Создаем заголовок
        self.create_header()

        # Создаем вкладки с заданиями
        self.create_tabs()

        self.setLayout(self.main_layout)

    def create_header(self):
        """Создание заголовка окна"""
        header_layout = QHBoxLayout()

        # Кнопка "Назад к меню"
        back_btn = QPushButton("← Назад к меню")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        back_btn.clicked.connect(self.back_to_menu)
        header_layout.addWidget(back_btn)

        # Заголовок
        title = QLabel("Задания по программированию")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-left: 20px;")
        header_layout.addWidget(title)

        # Растягиваем пространство
        header_layout.addStretch()

        self.main_layout.addLayout(header_layout)

    def create_tabs(self):
        """Создание вкладок с заданиями по темам"""
        try:
            print(f"DEBUG: Создание вкладок. Данные задач: {bool(self.tasks_data)}")

            if not self.tasks_data:
                print("ERROR: Данные задач пусты!")
                error_label = QLabel("Ошибка: данные задач не загружены")
                error_label.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
                self.main_layout.addWidget(error_label)
                return

            # Создаем виджет с вкладками
            tabs_widget = QTabWidget()
            tabs_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 2px solid #bdc3c7;
                    background-color: white;
                    border-radius: 5px;
                }
                QTabBar::tab {
                    background-color: #ecf0f1;
                    padding: 12px 25px;
                    margin-right: 2px;
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #2c3e50;
                    min-width: 120px;
                }
                QTabBar::tab:selected {
                    background-color: #3498db;
                    color: white;
                }
                QTabBar::tab:hover {
                    background-color: #d5dbdb;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
            """)

            # Создаем вкладку для каждой темы
            for theme_name, tasks in self.tasks_data.items():
                print(f"DEBUG: Создание вкладки для темы '{theme_name}' с {len(tasks)} задачами")

                # Создаем виджет для вкладки
                tab_widget = QWidget()
                tab_layout = QVBoxLayout()
                tab_layout.setContentsMargins(20, 20, 20, 20)
                tab_layout.setSpacing(15)

                # Создаем секцию темы
                self.create_theme_section(theme_name, tasks, tab_layout)

                # Добавляем растягивающееся пространство внизу
                tab_layout.addStretch()

                tab_widget.setLayout(tab_layout)
                tabs_widget.addTab(tab_widget, theme_name)

            self.main_layout.addWidget(tabs_widget)
            print("DEBUG: Вкладки созданы успешно")

        except Exception as e:
            print(f"ERROR в create_tabs: {e}")
            import traceback
            traceback.print_exc()

    def create_theme_section(self, theme_name, tasks, layout):
        """Создание секции для одной темы заданий"""
        try:
            print(f"DEBUG: Создание секции для темы '{theme_name}' с задачами: {list(tasks.keys())}")

            # Безопасное получение прогресса
            if self.progress_manager and not isinstance(self.progress_manager, MockProgressManager):
                completed_tasks, total_tasks = self.progress_manager.get_theme_progress(theme_name, len(tasks))
            else:
                completed_tasks, total_tasks = 0, len(tasks)

            progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

            # Заголовок темы с прогрессом
            theme_header = QHBoxLayout()

            theme_label = QLabel(theme_name)
            theme_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            theme_label.setStyleSheet("color: #2c3e50; padding: 10px 0;")
            theme_header.addWidget(theme_label)

            # ВСЕГДА показываем прогресс-бар
            progress_widget = QWidget()
            progress_layout = QVBoxLayout()
            progress_layout.setContentsMargins(0, 0, 0, 0)

            progress_label = QLabel(f"Прогресс: {completed_tasks}/{total_tasks} ({progress_percentage}%)")
            progress_label.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: bold;")
            progress_layout.addWidget(progress_label)

            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)
            progress_bar.setValue(progress_percentage)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    text-align: center;
                    font-weight: bold;
                    color: white;
                    height: 20px;
                    min-width: 200px;
                }
                QProgressBar::chunk {
                    background-color: #27ae60;
                    border-radius: 3px;
                }
            """)
            progress_layout.addWidget(progress_bar)

            # Кнопка сброса прогресса темы (только если progress_manager работает)
            if self.progress_manager and not isinstance(self.progress_manager, MockProgressManager):
                reset_theme_btn = QPushButton("🔄 Сбросить прогресс темы")
                reset_theme_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                reset_theme_btn.clicked.connect(lambda: self.reset_theme_progress(theme_name))
                progress_layout.addWidget(reset_theme_btn)

            progress_widget.setLayout(progress_layout)
            progress_widget.setFixedWidth(250)
            theme_header.addWidget(progress_widget)

            theme_header.addStretch()
            layout.addLayout(theme_header)

            # Добавляем разделитель
            separator = QLabel()
            separator.setStyleSheet("border-bottom: 1px solid #bdc3c7; margin: 10px 0;")
            separator.setFixedHeight(1)
            layout.addWidget(separator)

            # Создание области прокрутки для задач
            scroll_area = QScrollArea()
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #f1f1f1;
                    width: 10px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background: #888;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #555;
                }
            """)

            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout()
            scroll_layout.setSpacing(5)
            scroll_layout.setContentsMargins(0, 0, 0, 0)

            # Создание кнопок задач
            for i, (task_name, task_data) in enumerate(tasks.items()):
                print(f"DEBUG: Создание кнопки для задачи '{task_name}'")

                task_button = QPushButton(task_name)
                task_button.setCheckable(True)
                task_button.setMinimumHeight(50)

                # Безопасная проверка выполнения задачи
                is_completed = False
                if self.progress_manager and not isinstance(self.progress_manager, MockProgressManager):
                    is_completed = self.progress_manager.is_task_completed(theme_name, task_name)

                if is_completed:
                    # Стиль для выполненных задач
                    task_button.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            border: none;
                            padding: 15px;
                            text-align: left;
                            font-size: 14px;
                            border-radius: 5px;
                            margin: 2px 0;
                            min-height: 40px;
                        }
                        QPushButton:hover {
                            background-color: #229954;
                        }
                        QPushButton:checked {
                            background-color: #1e8449;
                        }
                    """)
                    task_button.setText(f"✅ {task_name}")
                else:
                    # Стиль для невыполненных задач
                    task_button.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            border: none;
                            padding: 15px;
                            text-align: left;
                            font-size: 14px;
                            border-radius: 5px;
                            margin: 2px 0;
                            min-height: 40px;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                        QPushButton:checked {
                            background-color: #21618c;
                        }
                    """)

                # Безопасный обработчик клика
                def create_handler(theme_name, task_data, button):
                    def handler():
                        try:
                            # Снимаем выделение с других кнопок
                            for j in range(scroll_layout.count()):
                                widget = scroll_layout.itemAt(j).widget()
                                if widget and widget != button and hasattr(widget, 'setChecked'):
                                    widget.setChecked(False)

                            button.setChecked(True)

                            # Отправляем сигнал
                            self.task_selected.emit(theme_name, task_data['name'], task_data['description'])

                        except Exception as e:
                            print(f"ERROR в обработчике задачи: {e}")

                    return handler

                task_button.clicked.connect(create_handler(theme_name, task_data, task_button))
                scroll_layout.addWidget(task_button)
                print(f"DEBUG: Кнопка '{task_name}' добавлена в layout")

            scroll_widget.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            scroll_area.setMaximumHeight(400)  # Увеличиваем высоту
            scroll_area.setMinimumHeight(200)  # Минимальная высота

            layout.addWidget(scroll_area)
            print(f"DEBUG: Секция '{theme_name}' создана с {scroll_layout.count()} кнопками")

        except Exception as e:
            print(f"ERROR в create_theme_section для '{theme_name}': {e}")
            import traceback
            traceback.print_exc()
            # Добавляем простую заглушку
            error_label = QLabel(f"Ошибка загрузки темы: {theme_name}")
            error_label.setStyleSheet("color: red; padding: 10px; font-size: 14px;")
            layout.addWidget(error_label)

    def reset_theme_progress(self, theme_name: str):
        """Сброс прогресса по теме"""
        if not self.progress_manager:
            QMessageBox.warning(self, "Ошибка", "Система прогресса недоступна")
            return

        try:
            reply = QMessageBox.question(
                self,
                'Сброс прогресса',
                f'Вы уверены, что хотите сбросить прогресс по теме "{theme_name}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.progress_manager.reset_theme_progress(theme_name)
                self.refresh_ui()
        except Exception as e:
            print(f"ERROR в reset_theme_progress: {e}")

    def refresh_ui(self):
        """Безопасное обновление интерфейса"""
        try:
            # Перезагружаем progress_manager
            self.load_progress_manager()

            # Очищаем текущий layout
            for i in reversed(range(self.main_layout.count())):
                child = self.main_layout.itemAt(i)
                if child.widget():
                    child.widget().setParent(None)
                elif child.layout():
                    self.clear_layout(child.layout())

            # Пересоздаем интерфейс
            self.create_header()
            self.create_tabs()

        except Exception as e:
            print(f"ERROR в refresh_ui: {e}")

    def clear_layout(self, layout):
        """Безопасная рекурсивная очистка layout"""
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().setParent(None)
                elif child.layout():
                    self.clear_layout(child.layout())
        except Exception as e:
            print(f"ERROR в clear_layout: {e}")

    def back_to_menu(self):
        """Возврат к главному меню"""
        self.main_window.show_menu()
