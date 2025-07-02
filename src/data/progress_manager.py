import json
import os
from typing import Dict, Set


class ProgressManager:
    def __init__(self):
        self.progress_file = os.path.join(os.path.dirname(__file__), 'user_progress.json')
        self.progress_data = self.load_progress()

    def load_progress(self) -> Dict[str, Set[str]]:
        """Загрузка прогресса из файла"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Преобразуем списки обратно в множества
                    return {theme: set(tasks) for theme, tasks in data.items()}
            return {}
        except Exception as e:
            print(f"Ошибка загрузки прогресса: {e}")
            return {}

    def save_progress(self):
        """Сохранение прогресса в файл"""
        try:
            # Создаем папку если её нет
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
            # Преобразуем множества в списки для JSON
            data = {theme: list(tasks) for theme, tasks in self.progress_data.items()}
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения прогресса: {e}")

    def mark_task_completed(self, theme: str, task_name: str):
        """Отметить задачу как выполненную"""
        if theme not in self.progress_data:
            self.progress_data[theme] = set()
        self.progress_data[theme].add(task_name)
        self.save_progress()

    def is_task_completed(self, theme: str, task_name: str) -> bool:
        """Проверить, выполнена ли задача"""
        return theme in self.progress_data and task_name in self.progress_data[theme]

    def get_theme_progress(self, theme: str, total_tasks: int) -> tuple:
        """Получить прогресс по теме (выполнено, всего)"""
        completed = len(self.progress_data.get(theme, set()))
        return completed, total_tasks

    def reset_progress(self):
        """Сброс всего прогресса"""
        self.progress_data = {}
        self.save_progress()

    def reset_theme_progress(self, theme: str):
        """Сброс прогресса по конкретной теме"""
        if theme in self.progress_data:
            del self.progress_data[theme]
            self.save_progress()


# Глобальный экземпляр
progress_manager = ProgressManager()
