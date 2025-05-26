from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsScene, QGraphicsPathItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath, QPolygonF
from typing import Any, Dict, List, Optional



class SimpleVariableWidget:
    """Простой виджет для переменной"""

    def __init__(self, scene, name: str, value: Any, x: float, y: float):
        self.scene = scene
        self.name = name
        self.value = value

        # Создаем прямоугольник
        self.rect = QGraphicsRectItem(x, y, 90, 35)
        self.rect.setPen(QPen(QColor("#2c3e50"), 2))
        self.rect.setBrush(QBrush(QColor("#3498db")))

        # Создаем текст для имени (уменьшенный шрифт)
        self.name_text = QGraphicsTextItem(name)
        self.name_text.setPos(x + 3, y + 2)
        self.name_text.setDefaultTextColor(QColor("white"))
        font = QFont("Arial", 8, QFont.Weight.Bold)
        self.name_text.setFont(font)

        # Создаем текст для значения (уменьшенный шрифт)
        value_str = str(value)
        if len(value_str) > 12:
            value_str = value_str[:10] + ".."

        self.value_text = QGraphicsTextItem(value_str)
        self.value_text.setPos(x + 3, y + 17)
        self.value_text.setDefaultTextColor(QColor("#ecf0f1"))
        value_font = QFont("Arial", 7)
        self.value_text.setFont(value_font)

        # Добавляем на сцену
        scene.addItem(self.rect)
        scene.addItem(self.name_text)
        scene.addItem(self.value_text)

    def remove_from_scene(self):
        """Удаление виджета со сцены"""
        self.scene.removeItem(self.rect)
        self.scene.removeItem(self.name_text)
        self.scene.removeItem(self.value_text)

    def update_value(self, new_value):
        """Обновление значения"""
        self.value = new_value
        value_str = str(new_value)
        if len(value_str) > 12:
            value_str = value_str[:10] + ".."
        self.value_text.setPlainText(value_str)


class SimpleListWidget:
    """Простой виджет для списка"""

    def __init__(self, scene, name: str, items: list, x: float, y: float):
        self.scene = scene
        self.name = name
        self.items = items
        self.elements = []

        # Уменьшенные размеры
        visible_items = min(len(items), 5)
        cell_width = 30
        total_width = visible_items * cell_width + 8

        # Главный прямоугольник
        self.main_rect = QGraphicsRectItem(x, y, total_width, 55)
        self.main_rect.setPen(QPen(QColor("#c0392b"), 2))
        self.main_rect.setBrush(QBrush(QColor("#e74c3c")))

        # Заголовок (уменьшенный шрифт)
        title = f"{name}[{len(items)}]"
        self.title_text = QGraphicsTextItem(title)
        self.title_text.setPos(x + 3, y + 2)
        self.title_text.setDefaultTextColor(QColor("white"))
        font = QFont("Arial", 7, QFont.Weight.Bold)
        self.title_text.setFont(font)

        # Добавляем на сцену
        scene.addItem(self.main_rect)
        scene.addItem(self.title_text)
        self.elements.extend([self.main_rect, self.title_text])

        # Создаем ячейки для элементов (уменьшенные)
        for i in range(visible_items):
            cell_x = x + i * cell_width + 4
            cell_y = y + 18

            # Ячейка
            cell_rect = QGraphicsRectItem(cell_x, cell_y, cell_width - 2, 32)
            cell_rect.setPen(QPen(QColor("white"), 1))
            cell_rect.setBrush(QBrush(QColor("#c0392b")))

            # Индекс (уменьшенный шрифт)
            index_text = QGraphicsTextItem(str(i))
            index_text.setPos(cell_x + 2, cell_y + 1)
            index_text.setDefaultTextColor(QColor("white"))
            index_text.setFont(QFont("Arial", 6))

            # Значение (уменьшенный шрифт)
            value_str = str(items[i])
            if len(value_str) > 4:
                value_str = value_str[:3] + ".."

            value_text = QGraphicsTextItem(value_str)
            value_text.setPos(cell_x + 2, cell_y + 15)
            value_text.setDefaultTextColor(QColor("white"))
            value_text.setFont(QFont("Arial", 6))

            # Добавляем на сцену
            scene.addItem(cell_rect)
            scene.addItem(index_text)
            scene.addItem(value_text)
            self.elements.extend([cell_rect, index_text, value_text])

    def remove_from_scene(self):
        """Удаление виджета со сцены"""
        for element in self.elements:
            self.scene.removeItem(element)


class SimpleVisualizationScene(QGraphicsScene):
    """Простая сцена визуализации"""

    def __init__(self):
        super().__init__()

        # Настройки сцены
        self.setSceneRect(0, 0, 800, 600)
        self.setBackgroundBrush(QBrush(QColor("#ffffff")))

        # Хранилище виджетов
        self.widgets = {}

        # Позиции (уменьшенные отступы)
        self.variable_positions = [(30, 30 + i * 45) for i in range(12)]
        self.list_positions = [(150, 30 + i * 65) for i in range(10)]

    def clear_all_widgets(self):
        """Очистка всех виджетов"""
        for widget in self.widgets.values():
            widget.remove_from_scene()
        self.widgets.clear()

    def update_variables(self, variables: Dict[str, Any]):
        """Обновление отображения переменных"""
        # Удаляем старые виджеты
        self.clear_all_widgets()

        # Разделяем переменные
        simple_vars = {}
        lists = {}
        dicts = {}

        for name, value in variables.items():
            if isinstance(value, list):
                lists[name] = value
            elif isinstance(value, dict):
                dicts[name] = value
            else:
                simple_vars[name] = value

        # Размещаем простые переменные
        var_index = 0
        for name, value in simple_vars.items():
            if var_index < len(self.variable_positions):
                x, y = self.variable_positions[var_index]
                widget = SimpleVariableWidget(self, name, value, x, y)
                self.widgets[name] = widget
                var_index += 1

        # Размещаем списки и словари
        list_index = 0
        for name, items in {**lists, **dicts}.items():
            if list_index < len(self.list_positions):
                x, y = self.list_positions[list_index]
                if isinstance(items, list):
                    widget = SimpleListWidget(self, name, items, x, y)
                else:
                    # Для словарей пока используем список ключей
                    widget = SimpleListWidget(self, name, list(items.keys()), x, y)
                self.widgets[name] = widget
                list_index += 1
