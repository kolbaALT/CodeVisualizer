from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                             QPushButton, QLabel, QGraphicsView, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from src.executor.code_executor import CodeExecutor
from src.visualizer.pythontutor_widgets import PythonTutorScene

from PyQt6.QtSvg import QSvgGenerator
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QRectF, QSize



class VisualizerWindow(QWidget):
    """Окно визуализатора кода"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.executor = CodeExecutor()
        self.current_step_number = -1
        self.visualization_scene = PythonTutorScene()
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

        # НОВОЕ: Настройка автодополнения
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
        """НОВЫЙ МЕТОД: Настройка автодополнения"""
        from PyQt6.Qsci import QsciAPIs

        # Создаем API для автодополнения
        lexer = self.code_editor.lexer()
        self.api = QsciAPIs(lexer)

        # Добавляем ключевые слова Python
        python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
            'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal',
            'not', 'or', 'pass', 'raise', 'return', 'try', 'while',
            'with', 'yield', 'True', 'False', 'None'
        ]

        for keyword_name in python_keywords:
            self.api.add(keyword_name)

        # Добавляем встроенные функции
        builtin_functions = [
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'dir',
            'enumerate', 'filter', 'float', 'format', 'hex', 'int',
            'isinstance', 'len', 'list', 'map', 'max', 'min', 'oct',
            'ord', 'pow', 'print', 'range', 'repr', 'reversed', 'round',
            'set', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip',
            'hasattr', 'getattr', 'setattr', 'super'
        ]

        for func_name in builtin_functions:
            self.api.add(func_name)

        # Подготавливаем API
        self.api.prepare()

        # Настраиваем автодополнение
        self.code_editor.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.code_editor.setAutoCompletionThreshold(2)  # Показывать после 2 символов
        self.code_editor.setAutoCompletionCaseSensitivity(False)
        self.code_editor.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)

    def setup_color_scheme(self):
        """Настройка цветовой схемы редактора"""
        # Основные цвета
        self.code_editor.setPaper(QColor("#2c3e50"))  # Фон
        self.code_editor.setColor(QColor("#ecf0f1"))  # Основной текст

        # Цвета для лексера Python
        lexer = self.code_editor.lexer()
        if lexer:
            # Комментарии
            lexer.setColor(QColor("#95a5a6"), QsciLexerPython.Comment)
            # Строки
            lexer.setColor(QColor("#e67e22"), QsciLexerPython.SingleQuotedString)
            lexer.setColor(QColor("#e67e22"), QsciLexerPython.DoubleQuotedString)
            # Ключевые слова
            lexer.setColor(QColor("#3498db"), QsciLexerPython.Keyword)
            # Числа
            lexer.setColor(QColor("#e74c3c"), QsciLexerPython.Number)
            # Операторы
            lexer.setColor(QColor("#f39c12"), QsciLexerPython.Operator)
            # Функции
            lexer.setColor(QColor("#9b59b6"), QsciLexerPython.FunctionMethodName)

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

        # КЛЮЧЕВЫЕ НАСТРОЙКИ для правильного отображения
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

        # Выравнивание по левому верхнему углу
        self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Отключаем полосы прокрутки для лучшего вида
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Устанавливаем фиксированную высоту для графической области
        self.graphics_view.setMinimumHeight(300)
        self.graphics_view.setMaximumHeight(400)

        viz_layout.addWidget(self.graphics_view)

        # Добавляем окно вывода
        output_label = QLabel("Вывод программы:")
        output_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        output_label.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")
        viz_layout.addWidget(output_label)

        # Импортируем QTextEdit локально
        from PyQt6.QtWidgets import QTextEdit

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

        viz_widget.setLayout(viz_layout)
        splitter.addWidget(viz_widget)

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
        self.step_back_btn.setEnabled(False)  # Пока отключена
        control_layout.addWidget(self.step_back_btn)

        # Кнопка "Шаг вперед"
        self.step_forward_btn = QPushButton("➡️ Шаг вперед")
        self.step_forward_btn.setStyleSheet(button_style)
        self.step_forward_btn.clicked.connect(self.step_forward)
        self.step_forward_btn.setEnabled(False)  # Пока отключена
        control_layout.addWidget(self.step_forward_btn)

        # Кнопка "Сброс"
        self.reset_btn = QPushButton("🔄 Сброс")
        self.reset_btn.setStyleSheet(
            button_style.replace("#3498db", "#e74c3c").replace("#2980b9", "#c0392b").replace("#21618c", "#a93226"))
        self.reset_btn.clicked.connect(self.reset_execution)
        control_layout.addWidget(self.reset_btn)

        # НОВЫЕ КНОПКИ ЭКСПОРТА
        # Кнопка "Экспорт PNG"
        self.export_png_btn = QPushButton("📷 PNG")
        self.export_png_btn.setStyleSheet(button_style.replace("#3498db", "#9b59b6"))
        self.export_png_btn.clicked.connect(self.export_to_png)
        control_layout.addWidget(self.export_png_btn)

        # Кнопка "Экспорт SVG"
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

    def back_to_menu(self):
        """Возврат к главному меню"""
        self.main_window.show_menu()

    def run_code(self):
        """Запуск кода"""
        # Получаем код из редактора
        code = self.code_editor.text()

        if not code.strip():
            self.line_indicator.setText("Ошибка: Код пустой")
            return

        # Очищаем окно вывода
        self.output_text.clear()

        try:
            # Выполняем код пошагово
            success = self.executor.execute_step_by_step(code)

            if success:
                # Переходим к первому шагу
                self.current_step_number = 0
                self.update_visualization()

                # Активируем кнопки навигации
                self.step_forward_btn.setEnabled(True)
                self.step_back_btn.setEnabled(False)  # На первом шаге назад нельзя

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

            # Обновляем состояние кнопок
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

            # Обновляем состояние кнопок
            self.step_back_btn.setEnabled(True)
            if self.current_step_number >= len(self.executor.steps) - 1:
                self.step_forward_btn.setEnabled(False)
        else:
            self.line_indicator.setText("Достигнут конец выполнения")

    def reset_execution(self):
        """Сброс выполнения"""
        self.executor.reset()
        self.current_step_number = -1

        # Отключаем кнопки навигации
        self.step_forward_btn.setEnabled(False)
        self.step_back_btn.setEnabled(False)

        # Очищаем визуализацию
        self.visualization_scene.clear_all()
        self.line_indicator.setText("Строка: не выполняется")

        # Очищаем окно вывода
        self.output_text.clear()

        # Убираем подсветку строк в редакторе
        self.code_editor.clearIndicatorRange(0, 0, self.code_editor.lines(), 0, 0)

    def update_visualization(self):
        """Обновление визуализации на основе текущего шага"""
        if self.current_step_number < 0 or self.current_step_number >= len(self.executor.steps):
            return

        # Получаем текущий шаг
        step = self.executor.steps[self.current_step_number]

        # ОТЛАДКА: Выводим информацию о текущем шаге
        print(f"DEBUG: Шаг {self.current_step_number}, строка {step.line_number}, код: {step.code_line}")
        print(f"DEBUG: Переменные: {step.variables}")

        # Обновляем индикатор строки
        self.line_indicator.setText(
            f"Строка: {step.line_number} | Шаг: {step.step_number + 1}/{len(self.executor.steps)}")

        # Подсвечиваем текущую строку в редакторе
        self.highlight_current_line(step.line_number)

        # Обновляем визуализацию переменных
        self.update_variables_display(step.variables)

        # Постепенно добавляем вывод
        self.update_output_display()

        # Если есть ошибка, показываем её
        if step.error:
            self.line_indicator.setText(f"ОШИБКА в строке {step.line_number}: {step.error}")

    def update_output_display(self):
        """Обновление окна вывода до текущего шага"""
        # Собираем весь вывод до текущего шага включительно
        output_text = ""

        for i in range(self.current_step_number + 1):
            if i < len(self.executor.steps):
                step = self.executor.steps[i]
                if step.output:
                    output_text += step.output + "\n"

        # Обновляем окно вывода
        self.output_text.setPlainText(output_text.rstrip())

        # Прокручиваем вниз
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

    def highlight_current_line(self, line_number: int):
        """Подсветка текущей строки в редакторе"""
        # Убираем предыдущую подсветку
        self.code_editor.clearIndicatorRange(0, 0, self.code_editor.lines(), 0, 0)

        # Подсвечиваем текущую строку (нумерация с 0)
        if line_number > 0:
            self.code_editor.setCursorPosition(line_number - 1, 0)
            self.code_editor.setSelection(line_number - 1, 0, line_number - 1,
                                          len(self.code_editor.text(line_number - 1)))

    def update_variables_display(self, variables: dict):
        """Обновление отображения переменных"""
        if not variables:
            self.visualization_scene.clear_all()
            return

        # Обновляем визуализацию в стиле Python Tutor
        self.visualization_scene.update_visualization(variables)

        # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Правильное масштабирование
        # Получаем границы всех элементов
        items_rect = self.visualization_scene.itemsBoundingRect()

        # Если есть элементы, подгоняем под них
        if not items_rect.isEmpty():
            # Добавляем отступы
            margin = 50
            expanded_rect = items_rect.adjusted(-margin, -margin, margin, margin)

            # Устанавливаем размер сцены
            self.visualization_scene.setSceneRect(expanded_rect)

            # Подгоняем вид под содержимое
            self.graphics_view.fitInView(expanded_rect, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            # Если элементов нет, устанавливаем стандартный размер
            self.visualization_scene.setSceneRect(0, 0, 800, 600)
            self.graphics_view.fitInView(0, 0, 800, 600, Qt.AspectRatioMode.KeepAspectRatio)

    def set_task_description(self, theme: str, task_name: str, description: str):
        """Установка описания задания под окном вывода"""
        # Создаем область описания задания если её нет
        if not hasattr(self, 'task_description'):
            self.create_task_description_area()

        # Устанавливаем текст задания
        task_text = f"""
    <h3 style="color: #2c3e50;">📝 {task_name}</h3>
    <p style="color: #34495e;"><strong>Тема:</strong> {theme}</p>
    <p style="color: #7f8c8d;">{description}</p>
    <hr>
    <p style="color: #27ae60; font-weight: bold;">💡 Напишите код выше и нажмите F5 для запуска!</p>
        """

        self.task_description.setHtml(task_text)
        self.task_description.show()

    def create_task_description_area(self):
        """Создание области описания задания"""
        from PyQt6.QtWidgets import QTextEdit

        # Находим layout с окном вывода
        viz_layout = self.graphics_view.parent().layout()

        # Создаем область описания задания
        task_label = QLabel("Описание задания:")
        task_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        task_label.setStyleSheet("color: #2c3e50; margin-top: 10px; margin-bottom: 5px;")

        self.task_description = QTextEdit()
        self.task_description.setMaximumHeight(150)
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

        # Добавляем в layout после окна вывода
        viz_layout.addWidget(task_label)
        viz_layout.addWidget(self.task_description)

    def export_to_png(self):
        """Экспорт визуализации в PNG"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить как PNG",
            "visualization.png",
            "PNG файлы (*.png);;Все файлы (*)"
        )

        if file_path:
            try:
                scene_rect = self.visualization_scene.itemsBoundingRect()
                if scene_rect.isEmpty():
                    scene_rect = QRectF(0, 0, 800, 600)

                pixmap = QPixmap(int(scene_rect.width() + 100), int(scene_rect.height() + 100))
                pixmap.fill()  # Белый фон

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
            self,
            "Сохранить как SVG",
            "visualization.svg",
            "SVG файлы (*.svg);;Все файлы (*)"
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



