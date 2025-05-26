import ast
import symtable
from typing import List, Dict, Any, Optional, Tuple


class CodeAnalysisError(Exception):
    """Исключение для ошибок анализа кода"""
    pass


class CodeParser:
    """Парсер и анализатор Python кода"""

    # Запрещенные узлы AST для безопасности
    FORBIDDEN_NODES = {
        ast.Import: "Импорт модулей запрещен",
        ast.ImportFrom: "Импорт из модулей запрещен",
        ast.Delete: "Оператор del запрещен",
        ast.Global: "Оператор global запрещен",
        ast.Nonlocal: "Оператор nonlocal запрещен",
    }

    # Запрещенные функции
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', 'compile', 'open', 'input',
        '__import__', 'getattr', 'setattr', 'delattr',
        'globals', 'locals', 'vars', 'dir'
    }

    def __init__(self):
        self.errors = []
        self.warnings = []

    def parse_code(self, code: str) -> Optional[ast.AST]:
        """
        Парсинг кода в AST с проверкой синтаксиса

        Args:
            code: Исходный код Python

        Returns:
            AST дерево или None при ошибке
        """
        self.errors.clear()
        self.warnings.clear()

        try:
            # Парсим код в AST
            tree = ast.parse(code)
            return tree
        except SyntaxError as e:
            error_msg = f"Синтаксическая ошибка в строке {e.lineno}: {e.msg}"
            self.errors.append(error_msg)
            return None
        except Exception as e:
            error_msg = f"Ошибка парсинга: {str(e)}"
            self.errors.append(error_msg)
            return None

    def validate_code(self, code: str) -> Tuple[bool, List[str], List[str]]:
        """
        Полная валидация кода

        Args:
            code: Исходный код Python

        Returns:
            Кортеж (валиден ли код, список ошибок, список предупреждений)
        """
        # Парсим код
        tree = self.parse_code(code)
        if tree is None:
            return False, self.errors, self.warnings

        # Проверяем на запрещенные конструкции
        self._check_forbidden_constructs(tree)

        # Проверяем символы
        self._check_symbols(code)

        # Возвращаем результат
        is_valid = len(self.errors) == 0
        return is_valid, self.errors.copy(), self.warnings.copy()

    def _check_forbidden_constructs(self, tree: ast.AST):
        """Проверка на запрещенные конструкции AST"""
        for node in ast.walk(tree):
            # Проверяем запрещенные типы узлов
            for forbidden_type, message in self.FORBIDDEN_NODES.items():
                if isinstance(node, forbidden_type):
                    line_num = getattr(node, 'lineno', 'неизвестно')
                    self.errors.append(f"Строка {line_num}: {message}")

            # Проверяем вызовы запрещенных функций
            if isinstance(node, ast.Call):
                self._check_function_call(node)

    def _check_function_call(self, node: ast.Call):
        """Проверка вызовов функций на запрещенные"""
        func_name = None

        # Получаем имя функции
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Проверяем, запрещена ли функция
        if func_name in self.FORBIDDEN_FUNCTIONS:
            line_num = getattr(node, 'lineno', 'неизвестно')
            self.errors.append(f"Строка {line_num}: Функция '{func_name}' запрещена")

    def _check_symbols(self, code: str):
        """Проверка символов с помощью symtable"""
        try:
            # Создаем таблицу символов
            table = symtable.symtable(code, '<string>', 'exec')

            # Можно добавить дополнительные проверки символов здесь
            # Например, проверка на неиспользуемые переменные

        except Exception as e:
            self.warnings.append(f"Предупреждение при анализе символов: {str(e)}")

    def get_variables(self, tree: ast.AST) -> List[str]:
        """Получение списка переменных из AST"""
        variables = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                variables.add(node.id)

        return sorted(list(variables))

    def get_functions(self, tree: ast.AST) -> List[str]:
        """Получение списка определенных функций"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return functions

    def get_imports(self, tree: ast.AST) -> List[str]:
        """Получение списка импортов (для информации)"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        return imports


# Функция для быстрой проверки кода
def quick_validate(code: str) -> Dict[str, Any]:
    """
    Быстрая валидация кода

    Args:
        code: Исходный код Python

    Returns:
        Словарь с результатами валидации
    """
    parser = CodeParser()
    is_valid, errors, warnings = parser.validate_code(code)

    result = {
        'valid': is_valid,
        'errors': errors,
        'warnings': warnings,
        'variables': [],
        'functions': []
    }

    # Если код валиден, получаем дополнительную информацию
    if is_valid:
        tree = parser.parse_code(code)
        if tree:
            result['variables'] = parser.get_variables(tree)
            result['functions'] = parser.get_functions(tree)

    return result
