import sys
import types
from typing import Set, Dict, Any, Optional
from importlib import import_module


class SecurityManager:
    """Менеджер безопасности для контроля импортов и выполнения кода"""

    # Белый список разрешенных модулей (безопасные для обучения)
    ALLOWED_MODULES = {
        # Математические модули
        'math', 'cmath', 'decimal', 'fractions', 'statistics',

        # Работа с данными
        'random', 'itertools', 'functools', 'operator',
        'collections', 'heapq', 'bisect',

        # Работа со строками и текстом
        're', 'string', 'textwrap',

        # Дата и время
        'datetime', 'time', 'calendar',

        # Работа с JSON
        'json',

        # Копирование объектов
        'copy',

        # Встроенные типы данных
        'enum', 'dataclasses',

        # Для продвинутых пользователей (опционально)
        # 'numpy', 'pandas', 'matplotlib.pyplot'
    }

    # Разрешенные подмодули (например, random.randint)
    ALLOWED_SUBMODULES = {
        'random.randint', 'random.choice', 'random.shuffle', 'random.sample',
        'datetime.datetime', 'datetime.date', 'datetime.time',
        'collections.defaultdict', 'collections.Counter', 'collections.deque',
        'itertools.combinations', 'itertools.permutations', 'itertools.product',
        'math.pi', 'math.e'
    }

    # Полностью запрещенные модули (опасные)
    FORBIDDEN_MODULES = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'pickle', 'marshal', 'shelve', 'dbm',
        'importlib', '__builtin__', 'builtins',
        'ctypes', 'multiprocessing', 'threading',
        'tempfile', 'shutil', 'glob', 'pathlib',
        'io', 'codecs', 'locale'
    }

    def __init__(self):
        self.original_import = None
        self.imported_modules = {}
        self.operation_count = 0
        self.max_operations = 10000  # Лимит операций для предотвращения зависания

    def setup_secure_environment(self):
        """Настройка безопасного окружения выполнения"""
        # Сохраняем оригинальную функцию импорта
        self.original_import = __builtins__.__import__

        # Заменяем на нашу безопасную версию
        __builtins__.__import__ = self._secure_import

        # Очищаем опасные модули из sys.modules
        self._clean_dangerous_modules()

    def restore_environment(self):
        """Восстановление оригинального окружения"""
        if self.original_import:
            __builtins__.__import__ = self.original_import

    def _secure_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Безопасная функция импорта с проверкой белого списка"""
        # Проверяем, разрешен ли модуль
        if not self._is_module_allowed(name):
            raise ImportError(f"Модуль '{name}' запрещен для импорта")

        # Проверяем fromlist (для импортов типа "from module import something")
        if fromlist:
            for item in fromlist:
                full_name = f"{name}.{item}"
                if not self._is_submodule_allowed(full_name):
                    raise ImportError(f"Импорт '{full_name}' запрещен")

        try:
            # Используем оригинальную функцию импорта
            module = self.original_import(name, globals, locals, fromlist, level)

            # Сохраняем информацию об импортированном модуле
            self.imported_modules[name] = module

            return module

        except Exception as e:
            raise ImportError(f"Ошибка импорта модуля '{name}': {str(e)}")

    def _is_module_allowed(self, module_name: str) -> bool:
        """Проверка, разрешен ли модуль для импорта"""
        # Проверяем точное совпадение
        if module_name in self.ALLOWED_MODULES:
            return True

        # Проверяем, не является ли модуль запрещенным
        if module_name in self.FORBIDDEN_MODULES:
            return False

        # Проверяем подмодули разрешенных модулей
        for allowed in self.ALLOWED_MODULES:
            if module_name.startswith(f"{allowed}."):
                return True

        return False

    def _is_submodule_allowed(self, full_name: str) -> bool:
        """Проверка, разрешен ли конкретный подмодуль"""
        return full_name in self.ALLOWED_SUBMODULES

    def _clean_dangerous_modules(self):
        """Удаление опасных модулей из sys.modules"""
        modules_to_remove = []

        for module_name in sys.modules:
            if any(module_name.startswith(forbidden) for forbidden in self.FORBIDDEN_MODULES):
                modules_to_remove.append(module_name)

        for module_name in modules_to_remove:
            if module_name in sys.modules:
                del sys.modules[module_name]

    def increment_operation_count(self):
        """Увеличение счетчика операций"""
        self.operation_count += 1
        if self.operation_count > self.max_operations:
            raise RuntimeError("Превышен лимит операций. Возможно, бесконечный цикл.")

    def reset_operation_count(self):
        """Сброс счетчика операций"""
        self.operation_count = 0

    def get_allowed_modules_info(self) -> Dict[str, Any]:
        """Получение информации о разрешенных модулях"""
        return {
            'allowed_modules': sorted(list(self.ALLOWED_MODULES)),
            'allowed_submodules': sorted(list(self.ALLOWED_SUBMODULES)),
            'forbidden_modules': sorted(list(self.FORBIDDEN_MODULES)),
            'total_allowed': len(self.ALLOWED_MODULES),
            'imported_modules': list(self.imported_modules.keys())
        }


# Глобальный экземпляр менеджера безопасности
security_manager = SecurityManager()


def create_safe_globals() -> Dict[str, Any]:
    """Создание безопасного глобального пространства имен"""
    safe_globals = {
        '__builtins__': {
            # Разрешенные встроенные функции
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'divmod',
            'enumerate', 'filter', 'float', 'format', 'frozenset', 'hex',
            'int', 'isinstance', 'issubclass', 'len', 'list', 'map', 'max',
            'min', 'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed',
            'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type',
            'zip'
        }
    }

    return safe_globals


def get_safe_builtins():
    """Получение безопасных встроенных функций"""
    import builtins

    safe_names = {
        'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'divmod',
        'enumerate', 'filter', 'float', 'format', 'frozenset', 'hex',
        'int', 'isinstance', 'issubclass', 'len', 'list', 'map', 'max',
        'min', 'oct', 'ord', 'pow', 'print', 'range', 'repr', 'reversed',
        'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple', 'type',
        'zip'
    }

    # Создаем объект-заглушку для builtins
    class SafeBuiltins:
        def __init__(self):
            # Добавляем безопасные функции
            for name in safe_names:
                if hasattr(builtins, name):
                    setattr(self, name, getattr(builtins, name))

            # Добавляем нашу безопасную функцию импорта
            self.__import__ = security_manager._secure_import

    return SafeBuiltins()

