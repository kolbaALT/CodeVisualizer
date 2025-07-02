import sys
import io
import contextlib
from typing import List, Dict, Any, Tuple
import json
import traceback


class TestCase:
    def __init__(self, inputs: List[str], expected_output: str, description: str = ""):
        self.inputs = inputs
        self.expected_output = expected_output.strip()
        self.description = description


class TestRunner:
    def __init__(self, security_manager):
        self.security_manager = security_manager
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
            with self._time_limit(self.max_execution_time):
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

    @contextlib.contextmanager
    def _time_limit(self, seconds):
        """Ограничение времени выполнения"""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Код выполнялся дольше {seconds} секунд")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
