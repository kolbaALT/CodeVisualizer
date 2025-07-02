from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QLabel, QGraphicsView,
                             QTextEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from src.executor.code_executor import CodeExecutor
from src.visualizer.pythontutor_widgets import PythonTutorScene
from PyQt6.QtSvg import QSvgGenerator
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtCore import QRectF, QSize
import json
import os
import sys
import io
import contextlib
from typing import List, Dict, Any
import traceback


class TestCase:
    def __init__(self, inputs: List[str], expected_output: str, description: str = ""):
        self.inputs = inputs
        self.expected_output = expected_output.strip()
        self.description = description


class TestRunner:
    def __init__(self):
        self.max_execution_time = 5  # секунд

    def run_tests(self, code: str, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Запускает код против набора тестов"""
        results = {
            'passed': 0,
            'total': len(test_cases),
            'test_results': [],
            'success': False,
            'error': None
        }

        for i, test_case in enumerate(test_cases):
            try:
                result = self._run_single_test(code, test_case, i + 1)
                results['test_results'].append(result)
                if result['passed']:
                    results['passed'] += 1
            except Exception as e:
                results['test_results'].append({
                    'test_number': i + 1,
                    'passed': False,
                    'error': str(e),
                    'description': test_case.description
                })

        results['success'] = results['passed'] == results['total']
        return results

    def _run_single_test(self, code: str, test_case: TestCase, test_number: int) -> Dict[str, Any]:
        """Запускает один тест"""
        # Создаем mock для input()
        input_iterator = iter(test_case.inputs)

        def mock_input(prompt=""):
            try:
                value = next(input_iterator)
                return value
            except StopIteration:
                raise EOFError("No more input available")

        # Перехватываем stdout
        captured_output = io.StringIO()

        # Создаем безопасное окружение
        safe_globals = {
            '__builtins__': {
                'print': lambda *args, **kwargs: print(*args, file=captured_output, **kwargs),
                'input': mock_input,
                'len': len,
                'range': range,
                'int': int,
                'float': float,
                'str': str,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'bool': bool,
                'abs': abs,
                'max': max,
                'min': min,
                'sum': sum,
                'sorted': sorted,
                'reversed': reversed,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
            }
        }

        try:
            # Выполняем код с ограничениями
            exec(code, safe_globals)

            # Получаем вывод
            actual_output = captured_output.getvalue().strip()

            # Сравниваем результаты
            passed = actual_output == test_case.expected_output

            return {
                'test_number': test_number,
                'passed': passed,
                'input': test_case.inputs,
                'expected_output': test_case.expected_output,
                'actual_output': actual_output,
                'description': test_case.description,
                'error': None
            }

        except Exception as e:
            return {
                'test_number': test_number,
                'passed': False,
                'input': test_case.inputs,
                'expected_output': test_case.expected_output,
                'actual_output': captured_output.getvalue().strip(),
                'description': test_case.description,
                'error': str(e)
            }


class VisualizerWindow(QWidget):
    """Окно визуализатора кода"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.executor = CodeExecutor()
        self.current_step_number = -1
        self.visualization_scene = PythonTutorScene()

        # Система тестирования
        self.test_runner = TestRunner()
        self.current_task_tests = []

        self.init_ui()

    def init_ui(self):
        """Создание интерфейса визуализатора"""
        # Основной вертикальный layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        self.create_header(main_layout)

        # Основная рабочая область (разделенная на две панели)
        self.create_work_area(main_layout)

        # Панель управления
        self.create_control_panel(main_layout)

        self.setLayout(main_layout)

    def create_header(self, layout):
        """Создание заголовка с кнопкой возврата"""
        header_layout = QHBoxLayout()

        # Кнопка "Назад к меню"
        back_btn = QPushButton("← Назад к меню")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 15px;
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
        title = QLabel("Визуализатор кода")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-left: 20px;")
        header_layout.addWidget(title)

        # Растягиваем пространство
        header_layout.addStretch()

        layout.addLayout(header_layout)

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
            if hasattr(self, 'tasks_window'):
                self.tasks_window.refresh_ui()

    def create_work_area(self, layout):
        """Создание основной рабочей области"""
        # Горизонтальный разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - редактор кода
        self.create_code_editor(splitter)

        # Правая панель - визуализация
        self.create_visualization_area(splitter)

        # Устанавливаем пропорции (40% код, 60% визуализация)
        splitter.setSizes([400, 600])

        layout.addWidget(splitter)

    def create_code_editor(self, splitter):
        """Создание области редактора кода с QScintilla"""
        code_widget = QWidget()
        code_layout = QVBoxLayout()

        # Заголовок панели
        code_label = QLabel("Редактор кода")
        code_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        code_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        code_layout.addWidget(code_label)

        # Создаем продвинутый редактор кода
        self.code_editor = QsciScintilla()

        # Настройка лексера Python для подсветки синтаксиса
        lexer = QsciLexerPython()
        lexer.setDefaultFont(QFont("Courier New", 12))
        self.code_editor.setLexer(lexer)

        # Настройки редактора
        self.setup_editor_settings()

        # Добавляем пример кода
        example_code = """# Простой пример для тестирования
x = 5
y = 10
result = x + y
print(f"Результат: {result}")

numbers = [1, 2, 3]
for num in numbers:
    print(num)"""

        self.code_editor.setText(example_code)
        code_layout.addWidget(self.code_editor)

        code_widget.setLayout(code_layout)
        splitter.addWidget(code_widget)

    def setup_editor_settings(self):
        """Настройка параметров редактора"""
        # Настройка шрифта
        font = QFont("Courier New", 12)
        font.setFixedPitch(True)

        # Применяем шрифт к лексеру
        lexer = self.code_editor.lexer()
        lexer.setFont(font)

        # Настройка автодополнения
        self.setup_autocompletion()

        # Настройка отступов
        self.code_editor.setIndentationsUseTabs(False)
        self.code_editor.setIndentationWidth(4)
        self.code_editor.setAutoIndent(True)

        # Показываем номера строк
        self.code_editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.code_editor.setMarginWidth(0, "0000")
        self.code_editor.setMarginLineNumbers(0, True)
        self.code_editor.setMarginsBackgroundColor(QColor("#f8f9fa"))
        self.code_editor.setMarginsForegroundColor(QColor("#7f8c8d"))

        # Подсветка текущей строки
        self.code_editor.setCaretLineVisible(True)
        self.code_editor.setCaretLineBackgroundColor(QColor("#ecf0f1"))

        # Скобки
        self.code_editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        # Настройка выделения
        self.code_editor.setSelectionBackgroundColor(QColor("#3498db"))

        # Настройка табуляции
        self.code_editor.setTabWidth(4)

    def setup_autocompletion(self):
        """Настройка автодополнения"""
        # Создаем API для автодополнения
        lexer = self.code_editor.lexer()
        self.api = QsciAPIs(lexer)

        # Добавляем ключевые слова Python
        python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield', 'True', 'False', 'None'
        ]

        for keyword in python_keywords:
            self.api.add(keyword)

        # Добавляем встроенные функции
        builtin_functions = [
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir', 'enumerate', 'filter', 'float', 'format', 'hex',
            'int', 'isinstance', 'len', 'list', 'map', 'max', 'min', 'oct', 'ord', 'pow', 'print', 'range', 'repr',
            'reversed', 'round', 'set', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip', 'hasattr', 'getattr', 'setattr',
            'super', 'input'
        ]

        for func in builtin_functions:
            self.api.add(func)

        # Подготавливаем API
        self.api.prepare()

        # Настраиваем автодополнение
        self.code_editor.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.code_editor.setAutoCompletionThreshold(2)
        self.code_editor.setAutoCompletionCaseSensitivity(False)
        self.code_editor.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)

    def create_visualization_area(self, splitter):
        """Создание области визуализации"""
        viz_widget = QWidget()
        viz_layout = QVBoxLayout()

        # Заголовок панели
        viz_label = QLabel("Визуализация")
        viz_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        viz_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        viz_layout.addWidget(viz_label)

        # Графическая область для визуализации
        self.graphics_view = QGraphicsView(self.visualization_scene)
        self.graphics_view.setStyleSheet("""
            QGraphicsView {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
        """)

        # Настройки для правильного отображения
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphics_view.setMinimumHeight(300)
        self.graphics_view.setMaximumHeight(400)

        viz_layout.addWidget(self.graphics_view)

        # Добавляем окно вывода
        output_label = QLabel("Вывод программы:")
        output_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        output_label.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")
        viz_layout.addWidget(output_label)

        # Текстовое поле для вывода
        self.output_text = QTextEdit()
        self.output_text.setMinimumHeight(100)
        self.output_text.setMaximumHeight(150)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid #34495e;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.output_text.setPlaceholderText("Здесь будет отображаться вывод print()...")
        self.output_text.setReadOnly(True)
        viz_layout.addWidget(self.output_text)

        # Область описания задания
        self.create_task_description_area(viz_layout)

        # Область результатов тестов
        self.create_test_results_area(viz_layout)

        viz_widget.setLayout(viz_layout)
        splitter.addWidget(viz_widget)

    def create_task_description_area(self, layout):
        """Создание области описания задания"""
        self.task_label = QLabel("Описание задания:")
        self.task_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.task_label.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")
        self.task_label.hide()  # Скрываем по умолчанию
        layout.addWidget(self.task_label)

        self.task_description = QTextEdit()
        self.task_description.setMaximumHeight(120)
        self.task_description.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 5px;
                padding: 10px;
                font-family: Arial;
                font-size: 11px;
            }
        """)
        self.task_description.setReadOnly(True)
        self.task_description.hide()  # Скрываем по умолчанию
        layout.addWidget(self.task_description)

    def create_test_results_area(self, layout):
        """Создание области результатов тестов"""
        self.test_results_area = QTextEdit()
        self.test_results_area.setReadOnly(True)
        self.test_results_area.setMaximumHeight(150)
        self.test_results_area.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        self.test_results_area.hide()  # Скрываем по умолчанию
        layout.addWidget(self.test_results_area)

    def create_control_panel(self, layout):
        """Создание панели управления"""
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 10, 0, 0)

        # Стиль для кнопок управления
        button_style = """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """

        # Кнопка "Запуск"
        self.run_btn = QPushButton("▶️ Запуск")
        self.run_btn.setStyleSheet(
            button_style.replace("#3498db", "#27ae60").replace("#2980b9", "#229954").replace("#21618c", "#1e8449"))
        self.run_btn.clicked.connect(self.run_code)
        control_layout.addWidget(self.run_btn)

        # Кнопка "Шаг назад"
        self.step_back_btn = QPushButton("⬅️ Шаг назад")
        self.step_back_btn.setStyleSheet(button_style)
        self.step_back_btn.clicked.connect(self.step_back)
        self.step_back_btn.setEnabled(False)
        control_layout.addWidget(self.step_back_btn)

        # Кнопка "Шаг вперед"
        self.step_forward_btn = QPushButton("➡️ Шаг вперед")
        self.step_forward_btn.setStyleSheet(button_style)
        self.step_forward_btn.clicked.connect(self.step_forward)
        self.step_forward_btn.setEnabled(False)
        control_layout.addWidget(self.step_forward_btn)

        # Кнопка "Сброс"
        self.reset_btn = QPushButton("🔄 Сброс")
        self.reset_btn.setStyleSheet(
            button_style.replace("#3498db", "#e74c3c").replace("#2980b9", "#c0392b").replace("#21618c", "#a93226"))
        self.reset_btn.clicked.connect(self.reset_execution)
        control_layout.addWidget(self.reset_btn)

        # Кнопка "Проверить решение"
        self.test_button = QPushButton("🧪 Проверить решение")
        self.test_button.setStyleSheet(
            button_style.replace("#3498db", "#28a745").replace("#2980b9", "#218838").replace("#21618c", "#1e7e34"))
        self.test_button.clicked.connect(self.run_tests)
        control_layout.addWidget(self.test_button)

        # Кнопки экспорта
        self.export_png_btn = QPushButton("📷 PNG")
        self.export_png_btn.setStyleSheet(button_style.replace("#3498db", "#9b59b6"))
        self.export_png_btn.clicked.connect(self.export_to_png)
        control_layout.addWidget(self.export_png_btn)

        self.export_svg_btn = QPushButton("🎨 SVG")
        self.export_svg_btn.setStyleSheet(button_style.replace("#3498db", "#8e44ad"))
        self.export_svg_btn.clicked.connect(self.export_to_svg)
        control_layout.addWidget(self.export_svg_btn)

        # Растягиваем пространство
        control_layout.addStretch()

        # Индикатор текущей строки
        self.line_indicator = QLabel("Строка: не выполняется")
        self.line_indicator.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        control_layout.addWidget(self.line_indicator)

        layout.addLayout(control_layout)

    def set_task_description(self, theme: str, task_name: str, description: str):
        """Установка описания задания и загрузка тестов"""
        # Сохраняем текущую задачу для отслеживания прогресса
        self.current_theme = theme
        self.current_task_name = task_name

        # Очищаем предыдущие результаты тестов
        self.test_results_area.hide()
        self.test_results_area.clear()

        # Показываем область описания задачи
        self.task_label.show()
        self.task_description.show()

        task_text = f"""<h3>{task_name}</h3>
    <p><strong>Тема:</strong> {theme}</p>
    <p>{description}</p>
    <p>💡 <em>Напишите код выше и нажмите "Проверить решение" для автоматической проверки!</em></p>"""

        self.task_description.setHtml(task_text)

        # Загружаем тесты для задачи
        self.load_task_tests(theme, task_name)

    def load_task_tests(self, theme: str, task_name: str):
        """Загружает тесты для задачи"""
        try:
            # Путь к файлу с тестами
            tests_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tasks_tests.json')

            if not os.path.exists(tests_file):
                print(f"Файл тестов не найден: {tests_file}")
                self.current_task_tests = []
                self.test_button.setText("🧪 Тесты не найдены")
                return

            with open(tests_file, 'r', encoding='utf-8') as f:
                tests_data = json.load(f)

            if theme in tests_data and task_name in tests_data[theme]:
                task_data = tests_data[theme][task_name]
                self.current_task_tests = [
                    TestCase(
                        inputs=test['inputs'],
                        expected_output=test['expected_output'],
                        description=test['description']
                    )
                    for test in task_data['test_cases']
                ]
                self.test_button.setText(f"🧪 Проверить решение ({len(self.current_task_tests)} тестов)")
            else:
                self.current_task_tests = []
                self.test_button.setText("🧪 Тесты не найдены")

        except Exception as e:
            print(f"Ошибка загрузки тестов: {e}")
            self.current_task_tests = []
            self.test_button.setText("🧪 Ошибка загрузки тестов")

    def run_tests(self):
        """Запускает тесты для текущего кода"""
        if not self.current_task_tests:
            self.test_results_area.setText("❌ Тесты не загружены для этой задачи")
            self.test_results_area.show()
            return

        code = self.code_editor.text()
        if not code.strip():
            self.test_results_area.setText("❌ Введите код для проверки")
            self.test_results_area.show()
            return

        # Запускаем тесты
        print("DEBUG: Запуск тестов...")
        results = self.test_runner.run_tests(code, self.current_task_tests)

        # Отображаем результаты
        self.display_test_results(results)

    def display_test_results(self, results: dict):
        """Отображает результаты тестирования"""
        self.test_results_area.show()

        if results['success']:
            header = f"✅ Все тесты пройдены! ({results['passed']}/{results['total']})"
            self.test_results_area.setStyleSheet("""
                QTextEdit {
                    background-color: #d4edda;
                    color: #155724;
                    border: 2px solid #c3e6cb;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                }
            """)
        else:
            header = f"❌ Тесты не пройдены ({results['passed']}/{results['total']})"
            self.test_results_area.setStyleSheet("""
                QTextEdit {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 2px solid #f5c6cb;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 10px;
                }
            """)

        output = [header, "=" * 60]

        for result in results['test_results']:
            test_num = result['test_number']
            status = "✅ ПРОЙДЕН" if result['passed'] else "❌ НЕ ПРОЙДЕН"

            output.append(f"\nТест {test_num}: {status}")
            if result['description']:
                output.append(f"Описание: {result['description']}")

            output.append(f"Входные данные: {result['input']}")
            output.append(f"Ожидаемый вывод: '{result['expected_output']}'")
            output.append(f"Ваш вывод: '{result['actual_output']}'")

            if result.get('error'):
                output.append(f"Ошибка: {result['error']}")

        self.test_results_area.setText('\n'.join(output))

    def back_to_menu(self):
        """Возврат к главному меню"""
        # Скрываем описание задачи при возврате в меню
        self.task_label.hide()
        self.task_description.hide()
        self.test_results_area.hide()

        # Очищаем текущую задачу
        if hasattr(self, 'current_theme'):
            delattr(self, 'current_theme')
        if hasattr(self, 'current_task_name'):
            delattr(self, 'current_task_name')

        self.main_window.show_menu()

    def run_code(self):
        """Запуск кода"""
        code = self.code_editor.text()
        if not code.strip():
            self.line_indicator.setText("Ошибка: Код пустой")
            return

        self.output_text.clear()

        try:
            success = self.executor.execute_step_by_step(code)
            if success:
                self.current_step_number = 0
                self.update_visualization()
                self.step_forward_btn.setEnabled(True)
                self.step_back_btn.setEnabled(False)
                self.line_indicator.setText(f"Выполнение начато. Шагов: {len(self.executor.steps)}")
            else:
                self.line_indicator.setText("Ошибка: Код содержит ошибки")
        except Exception as e:
            self.line_indicator.setText(f"Ошибка выполнения: {str(e)}")
            print(f"Ошибка при выполнении кода: {e}")

    def step_back(self):
        """Шаг назад"""
        if self.current_step_number > 0:
            self.current_step_number -= 1
            self.update_visualization()
            self.step_forward_btn.setEnabled(True)
            if self.current_step_number <= 0:
                self.step_back_btn.setEnabled(False)
        else:
            self.line_indicator.setText("Достигнуто начало выполнения")

    def step_forward(self):
        """Шаг вперед"""
        if self.current_step_number < len(self.executor.steps) - 1:
            self.current_step_number += 1
            self.update_visualization()
            self.step_back_btn.setEnabled(True)
            if self.current_step_number >= len(self.executor.steps) - 1:
                self.step_forward_btn.setEnabled(False)
        else:
            self.line_indicator.setText("Достигнут конец выполнения")

    def reset_execution(self):
        """Сброс выполнения"""
        self.executor.reset()
        self.current_step_number = -1
        self.step_forward_btn.setEnabled(False)
        self.step_back_btn.setEnabled(False)
        self.visualization_scene.clear_all()
        self.line_indicator.setText("Строка: не выполняется")
        self.output_text.clear()
        self.code_editor.clearIndicatorRange(0, 0, self.code_editor.lines(), 0, 0)

    def update_visualization(self):
        """Обновление визуализации на основе текущего шага"""
        if self.current_step_number < 0 or self.current_step_number >= len(self.executor.steps):
            return

        step = self.executor.steps[self.current_step_number]

        print(f"DEBUG: Шаг {self.current_step_number}, строка {step.line_number}, код: {step.code_line}")
        print(f"DEBUG: Переменные: {step.variables}")

        self.line_indicator.setText(
            f"Строка: {step.line_number} | Шаг: {step.step_number + 1}/{len(self.executor.steps)}")

        self.highlight_current_line(step.line_number)
        self.update_variables_display(step.variables)
        self.update_output_display()

        if step.error:
            self.line_indicator.setText(f"ОШИБКА в строке {step.line_number}: {step.error}")

    def update_output_display(self):
        """Обновление окна вывода до текущего шага"""
        output_text = ""
        for i in range(self.current_step_number + 1):
            if i < len(self.executor.steps):
                step = self.executor.steps[i]
                if step.output:
                    output_text += step.output + "\n"

        self.output_text.setPlainText(output_text.rstrip())
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

    def highlight_current_line(self, line_number: int):
        """Подсветка текущей строки в редакторе"""
        self.code_editor.clearIndicatorRange(0, 0, self.code_editor.lines(), 0, 0)
        if line_number > 0:
            self.code_editor.setCursorPosition(line_number - 1, 0)
            self.code_editor.setSelection(line_number - 1, 0, line_number - 1,
                                          len(self.code_editor.text(line_number - 1)))

    def update_variables_display(self, variables: dict):
        """Обновление отображения переменных"""
        if not variables:
            self.visualization_scene.clear_all()
            return

        self.visualization_scene.update_visualization(variables)

        items_rect = self.visualization_scene.itemsBoundingRect()
        if not items_rect.isEmpty():
            margin = 50
            expanded_rect = items_rect.adjusted(-margin, -margin, margin, margin)
            self.visualization_scene.setSceneRect(expanded_rect)
            self.graphics_view.fitInView(expanded_rect, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.visualization_scene.setSceneRect(0, 0, 800, 600)
            self.graphics_view.fitInView(0, 0, 800, 600, Qt.AspectRatioMode.KeepAspectRatio)

    def export_to_png(self):
        """Экспорт визуализации в PNG"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как PNG", "visualization.png", "PNG файлы (*.png);;Все файлы (*)"
        )
        if file_path:
            try:
                scene_rect = self.visualization_scene.itemsBoundingRect()
                if scene_rect.isEmpty():
                    scene_rect = QRectF(0, 0, 800, 600)

                pixmap = QPixmap(int(scene_rect.width() + 100), int(scene_rect.height() + 100))
                pixmap.fill()
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                self.visualization_scene.render(painter, QRectF(50, 50, scene_rect.width(), scene_rect.height()),
                                                scene_rect)
                painter.end()

                pixmap.save(file_path, "PNG")
                QMessageBox.information(self, "Экспорт завершен", f"Визуализация сохранена в:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка экспорта", f"Не удалось сохранить PNG:\n{str(e)}")

    def export_to_svg(self):
        """Экспорт визуализации в SVG"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как SVG", "visualization.svg", "SVG файлы (*.svg);;Все файлы (*)"
        )
        if file_path:
            try:
                scene_rect = self.visualization_scene.itemsBoundingRect()
                if scene_rect.isEmpty():
                    scene_rect = QRectF(0, 0, 800, 600)

                svg_generator = QSvgGenerator()
                svg_generator.setFileName(file_path)
                svg_generator.setSize(QSize(int(scene_rect.width() + 100), int(scene_rect.height() + 100)))
                svg_generator.setViewBox(QRectF(0, 0, scene_rect.width() + 100, scene_rect.height() + 100))
                svg_generator.setTitle("Python Code Visualization")
                svg_generator.setDescription("Визуализация выполнения кода Python")

                painter = QPainter(svg_generator)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                self.visualization_scene.render(painter, QRectF(50, 50, scene_rect.width(), scene_rect.height()),
                                                scene_rect)
                painter.end()

                QMessageBox.information(self, "Экспорт завершен", f"Визуализация сохранена в:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка экспорта", f"Не удалось сохранить SVG:\n{str(e)}")
