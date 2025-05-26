import sys
import copy
import traceback
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from src.core.security import security_manager, get_safe_builtins
from src.core.code_parser import CodeParser


@dataclass
class ExecutionStep:
    """Класс для хранения состояния одного шага выполнения"""
    step_number: int
    line_number: int
    code_line: str
    variables: Dict[str, Any]
    event_type: str  # 'line', 'call', 'return', 'exception'
    function_name: Optional[str] = None
    error: Optional[str] = None
    output: str = ""  # Поле для хранения вывода на этом шаге


class CodeExecutor:
    """Пошаговый исполнитель Python кода"""

    def __init__(self):
        self.steps: List[ExecutionStep] = []
        self.current_step = -1
        self.code_lines: List[str] = []
        self.is_running = False
        self.is_paused = False
        self.execution_globals = {}
        self.execution_locals = {}
        self.original_trace = None
        self.step_callback: Optional[Callable] = None
        self.max_steps = 1000  # Защита от бесконечных циклов

        # Парсер для валидации кода
        self.parser = CodeParser()

        # Система захвата print()
        self.print_outputs = []
        self.current_print_output = ""

    def prepare_code(self, code: str) -> bool:
        """
        Подготовка кода к выполнению

        Args:
            code: Исходный код Python

        Returns:
            True если код готов к выполнению, False при ошибках
        """
        # Валидация кода
        is_valid, errors, warnings = self.parser.validate_code(code)

        if not is_valid:
            print("Ошибки в коде:")
            for error in errors:
                print(f"  - {error}")
            return False

        if warnings:
            print("Предупреждения:")
            for warning in warnings:
                print(f"  - {warning}")

        # Разбиваем код на строки
        self.code_lines = code.strip().split('\n')

        # Очищаем предыдущие результаты
        self.steps.clear()
        self.current_step = -1
        self.print_outputs.clear()

        # Подготавливаем безопасное окружение
        self._setup_execution_environment()

        return True

    def _setup_execution_environment(self):
        """Настройка безопасного окружения выполнения"""
        security_manager.reset_operation_count()

        # Создаем расширенное безопасное окружение с поддержкой классов
        import builtins

        safe_builtins = {}
        safe_names = {
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'divmod',
            'enumerate', 'filter', 'float', 'format', 'frozenset', 'hex',
            'int', 'isinstance', 'issubclass', 'len', 'list', 'map', 'max',
            'min', 'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed',
            'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type',
            'zip', 'hasattr', 'getattr', 'setattr', 'delattr', 'dir',
            'super', 'property', 'staticmethod', 'classmethod'
        }

        for name in safe_names:
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)

        # КЛЮЧЕВОЕ ДОБАВЛЕНИЕ: Функции для работы с классами
        safe_builtins['__build_class__'] = builtins.__build_class__
        safe_builtins['__name__'] = '__main__'

        # Заменяем print на нашу версию
        safe_builtins['print'] = self._custom_print

        self.execution_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
        }

        # Локальные переменные
        self.execution_locals = {}

    def _custom_print(self, *args, **kwargs):
        """Кастомная функция print для захвата вывода"""
        # Формируем строку как обычный print
        import io
        output = io.StringIO()
        print(*args, file=output, **kwargs)
        result = output.getvalue().rstrip('\n')

        # Сохраняем вывод
        self.current_print_output = result

        # Также выводим в консоль для отладки
        print(*args, **kwargs)

    def execute_step_by_step(self, code: str) -> bool:
        """
        Выполнение кода пошагово

        Args:
            code: Исходный код Python

        Returns:
            True если выполнение началось успешно
        """
        if not self.prepare_code(code):
            return False

        try:
            # Компилируем код
            compiled_code = compile(code, '<string>', 'exec')

            # Устанавливаем трассировщик
            self.original_trace = sys.gettrace()
            sys.settrace(self._trace_function)

            self.is_running = True

            # Выполняем код
            exec(compiled_code, self.execution_globals, self.execution_locals)

            # НЕ ДОБАВЛЯЕМ финальный шаг - он вызывает проблемы
            # Вместо этого убеждаемся, что последний шаг содержит правильные данные

        except Exception as e:
            # Записываем ошибку как последний шаг
            error_step = ExecutionStep(
                step_number=len(self.steps),
                line_number=getattr(e, 'lineno', len(self.code_lines)),
                code_line="# Ошибка выполнения",
                variables={},
                event_type='exception',
                error=str(e)
            )
            self.steps.append(error_step)

        finally:
            # Восстанавливаем окружение
            self.is_running = False
            sys.settrace(self.original_trace)

        return True

    def _trace_function(self, frame, event, arg):
        """Функция трассировки для отслеживания выполнения"""
        # Защита от слишком большого количества шагов
        if len(self.steps) >= self.max_steps:
            raise RuntimeError("Превышено максимальное количество шагов выполнения")

        # Увеличиваем счетчик операций для защиты от зависания
        security_manager.increment_operation_count()

        # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Игнорируем события не из нашего кода
        if frame.f_code.co_filename != '<string>':
            return self._trace_function

        # ДОПОЛНИТЕЛЬНАЯ ФИЛЬТРАЦИЯ: Игнорируем системные вызовы
        if frame.f_code.co_name not in ['<module>', '__main__']:
            return self._trace_function

        # Обрабатываем только события 'line'
        if event != 'line':
            return self._trace_function

        line_number = frame.f_lineno

        # ВАЖНО: Проверяем, что номер строки в пределах нашего кода
        if line_number < 1 or line_number > len(self.code_lines):
            return self._trace_function

        # Получаем строку кода
        code_line = self.code_lines[line_number - 1].strip()

        # Получаем текущие переменные из frame.f_locals
        current_vars = {}

        try:
            for name, value in frame.f_locals.items():
                if not name.startswith('__'):
                    try:
                        if isinstance(value, (int, float, str, bool, type(None))):
                            current_vars[name] = value
                        elif isinstance(value, (list, dict, tuple, set)):
                            # Создаем копии для сохранения состояния НА ЭТОТ МОМЕНТ
                            if isinstance(value, list):
                                current_vars[name] = value.copy()
                            elif isinstance(value, dict):
                                current_vars[name] = value.copy()
                            elif isinstance(value, tuple):
                                current_vars[name] = tuple(value)
                            elif isinstance(value, set):
                                current_vars[name] = set(value)
                        else:
                            current_vars[name] = str(value)
                    except:
                        current_vars[name] = f"<{type(value).__name__}>"
        except:
            current_vars = {}

        # Проверяем, есть ли вывод от print на этом шаге
        step_output = ""
        if self.current_print_output:
            step_output = self.current_print_output
            self.current_print_output = ""

        # Создаем шаг выполнения
        step = ExecutionStep(
            step_number=len(self.steps),
            line_number=line_number,
            code_line=code_line,
            variables=current_vars,
            event_type=event,
            output=step_output
        )

        self.steps.append(step)

        # Вызываем callback если установлен
        if self.step_callback:
            self.step_callback(step)

        return self._trace_function

    def get_step(self, step_number: int) -> Optional[ExecutionStep]:
        """Получение конкретного шага выполнения"""
        if 0 <= step_number < len(self.steps):
            return self.steps[step_number]
        return None

    def get_current_step(self) -> Optional[ExecutionStep]:
        """Получение текущего шага"""
        return self.get_step(self.current_step)

    def next_step(self) -> Optional[ExecutionStep]:
        """Переход к следующему шагу"""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            return self.get_current_step()
        return None

    def prev_step(self) -> Optional[ExecutionStep]:
        """Переход к предыдущему шагу"""
        if self.current_step > 0:
            self.current_step -= 1
            return self.get_current_step()
        return None

    def goto_step(self, step_number: int) -> Optional[ExecutionStep]:
        """Переход к конкретному шагу"""
        if 0 <= step_number < len(self.steps):
            self.current_step = step_number
            return self.get_current_step()
        return None

    def reset(self):
        """Сброс состояния исполнителя"""
        self.steps.clear()
        self.current_step = -1
        self.code_lines.clear()
        self.is_running = False
        self.is_paused = False
        self.execution_globals.clear()
        self.execution_locals.clear()
        self.print_outputs.clear()
        self.current_print_output = ""

    def get_execution_summary(self) -> Dict[str, Any]:
        """Получение сводки выполнения"""
        return {
            'total_steps': len(self.steps),
            'current_step': self.current_step,
            'has_errors': any(step.error for step in self.steps),
            'variables_count': len(self.execution_locals),
            'code_lines': len(self.code_lines)
        }

    def set_step_callback(self, callback: Callable[[ExecutionStep], None]):
        """Установка callback функции для уведомления о новых шагах"""
        self.step_callback = callback


# Функция для быстрого тестирования
def quick_execute(code: str) -> List[ExecutionStep]:
    """
    Быстрое выполнение кода и получение всех шагов

    Args:
        code: Исходный код Python

    Returns:
        Список шагов выполнения
    """
    executor = CodeExecutor()
    if executor.execute_step_by_step(code):
        return executor.steps
    return []
