from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsScene, QGraphicsPathItem, QGraphicsItem
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainterPath
from typing import Any, Dict, List, Optional, Tuple


class FrameWidget:
    """Виджет для отображения фрейма (области переменных)"""

    def __init__(self, scene, frame_name: str, x: float, y: float):
        self.scene = scene
        self.frame_name = frame_name
        self.variables = {}
        self.elements = []

        # Размеры фрейма
        self.width = 180
        self.height = 40  # Начальная высота, будет расширяться
        self.x = x
        self.y = y

        # Создаем заголовок фрейма
        self.create_frame_header()

    def create_frame_header(self):
        """Создание заголовка фрейма"""
        # Фон заголовка
        header_rect = QGraphicsRectItem(self.x, self.y, self.width, 25)
        header_rect.setPen(QPen(QColor("#34495e"), 2))
        header_rect.setBrush(QBrush(QColor("#3498db")))

        # Текст заголовка
        header_text = QGraphicsTextItem(self.frame_name)
        header_text.setPos(self.x + 5, self.y + 2)
        header_text.setDefaultTextColor(QColor("white"))
        header_text.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(header_text)
        self.elements.extend([header_rect, header_text])

    def add_variable(self, name: str, value: Any, is_reference: bool = False) -> Tuple[float, float]:
        """Добавление переменной в фрейм"""
        var_y = self.y + 25 + len(self.variables) * 25

        # Фон переменной
        var_rect = QGraphicsRectItem(self.x, var_y, self.width, 25)
        var_rect.setPen(QPen(QColor("#bdc3c7"), 1))
        var_rect.setBrush(QBrush(QColor("#ecf0f1")))

        # Имя переменной
        name_text = QGraphicsTextItem(name)
        name_text.setPos(self.x + 5, var_y + 3)
        name_text.setDefaultTextColor(QColor("#2c3e50"))
        name_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

        # Добавляем основные элементы
        self.scene.addItem(var_rect)
        self.scene.addItem(name_text)
        self.elements.extend([var_rect, name_text])

        connection_point = None

        if is_reference:
            # Создаем точку для стрелки
            dot_x = self.x + self.width - 15
            dot_y = var_y + 12

            dot = QGraphicsRectItem(dot_x, dot_y, 6, 6)
            dot.setPen(QPen(QColor("#e74c3c"), 2))
            dot.setBrush(QBrush(QColor("#e74c3c")))

            self.scene.addItem(dot)
            self.elements.append(dot)

            # Возвращаем координаты точки для стрелки
            connection_point = (dot_x + 6, dot_y + 3)  # Правый край точки
        else:
            # Простое значение - отображаем его
            value_str = str(value)
            if len(value_str) > 15:
                value_str = value_str[:12] + "..."

            value_text = QGraphicsTextItem(value_str)
            value_text.setPos(self.x + self.width - 80, var_y + 3)
            value_text.setDefaultTextColor(QColor("#7f8c8d"))
            value_text.setFont(QFont("Arial", 8))

            self.scene.addItem(value_text)
            self.elements.append(value_text)

        self.variables[name] = {
            'value': value,
            'is_reference': is_reference,
            'connection_point': connection_point
        }

        # Увеличиваем высоту фрейма
        self.height = 25 + len(self.variables) * 25

        return connection_point if connection_point else (0, 0)

    def remove_from_scene(self):
        """Удаление фрейма со сцены"""
        for element in self.elements:
            self.scene.removeItem(element)
        self.elements.clear()
        self.variables.clear()


class ObjectWidget:
    """Виджет для отображения объекта в памяти"""

    def __init__(self, scene, obj_id: str, obj_type: str, content: Any, x: float, y: float):
        self.scene = scene
        self.obj_id = obj_id
        self.obj_type = obj_type
        self.content = content
        self.elements = []
        self.x = x
        self.y = y

        # Проверяем тип объекта
        if obj_type == "class_instance":
            # Это экземпляр пользовательского класса
            class_name = content.__class__.__name__
            self.class_widget = ClassInstanceWidget(scene, obj_id, content, class_name, x, y)
            return

        # Проверяем, есть ли вложенные структуры
        has_nested = self._has_nested_structures(content)

        if has_nested:
            self.create_nested_object(obj_type, content)
        elif obj_type == "list":
            self.create_list_object()
        elif obj_type == "dict":
            self.create_dict_object()
        else:
            self.create_simple_object()

    def _has_nested_structures(self, content: Any) -> bool:
        """Проверка наличия вложенных структур"""
        if isinstance(content, list):
            return any(isinstance(item, (list, dict)) for item in content)
        elif isinstance(content, dict):
            return any(isinstance(value, (list, dict)) for value in content.values())
        return False

    def create_list_object(self):
        """Создание объекта списка"""
        items = self.content if isinstance(self.content, list) else []
        visible_items = min(len(items), 5)

        # Размеры
        cell_width = 35
        total_width = max(visible_items * cell_width, 80)
        height = 70

        # Заголовок объекта
        header_rect = QGraphicsRectItem(self.x, self.y, total_width, 20)
        header_rect.setPen(QPen(QColor("#c0392b"), 2))
        header_rect.setBrush(QBrush(QColor("#e74c3c")))

        header_text = QGraphicsTextItem(f"list (len={len(items)})")
        header_text.setPos(self.x + 5, self.y + 2)
        header_text.setDefaultTextColor(QColor("white"))
        header_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(header_text)
        self.elements.extend([header_rect, header_text])

        # Элементы списка
        for i in range(visible_items):
            cell_x = self.x + i * cell_width
            cell_y = self.y + 20

            # Ячейка
            cell_rect = QGraphicsRectItem(cell_x, cell_y, cell_width, 45)
            cell_rect.setPen(QPen(QColor("#c0392b"), 1))
            cell_rect.setBrush(QBrush(QColor("#ecf0f1")))

            # Индекс
            index_text = QGraphicsTextItem(str(i))
            index_text.setPos(cell_x + 2, cell_y + 2)
            index_text.setDefaultTextColor(QColor("#2c3e50"))
            index_text.setFont(QFont("Arial", 7))

            # Разделительная линия
            line_rect = QGraphicsRectItem(cell_x + 2, cell_y + 18, cell_width - 4, 1)
            line_rect.setBrush(QBrush(QColor("#bdc3c7")))

            # Значение
            value_str = str(items[i])
            if len(value_str) > 4:
                value_str = value_str[:3] + ".."

            value_text = QGraphicsTextItem(value_str)
            value_text.setPos(cell_x + 2, cell_y + 22)
            value_text.setDefaultTextColor(QColor("#2c3e50"))
            value_text.setFont(QFont("Arial", 7))

            self.scene.addItem(cell_rect)
            self.scene.addItem(index_text)
            self.scene.addItem(line_rect)
            self.scene.addItem(value_text)
            self.elements.extend([cell_rect, index_text, line_rect, value_text])

        # Многоточие если нужно
        if len(items) > 5:
            dots_text = QGraphicsTextItem("...")
            dots_text.setPos(self.x + visible_items * cell_width + 5, self.y + 40)
            dots_text.setDefaultTextColor(QColor("#7f8c8d"))
            dots_text.setFont(QFont("Arial", 8))
            self.scene.addItem(dots_text)
            self.elements.append(dots_text)

    def create_dict_object(self):
        """Создание объекта словаря"""
        items = self.content if isinstance(self.content, dict) else {}
        visible_items = min(len(items), 4)

        # Размеры
        width = 120
        height = 20 + visible_items * 25

        # Заголовок объекта
        header_rect = QGraphicsRectItem(self.x, self.y, width, 20)
        header_rect.setPen(QPen(QColor("#8e44ad"), 2))
        header_rect.setBrush(QBrush(QColor("#9b59b6")))

        header_text = QGraphicsTextItem(f"dict (len={len(items)})")
        header_text.setPos(self.x + 5, self.y + 2)
        header_text.setDefaultTextColor(QColor("white"))
        header_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(header_text)
        self.elements.extend([header_rect, header_text])

        # Элементы словаря
        for i, (key, value) in enumerate(list(items.items())[:visible_items]):
            item_y = self.y + 20 + i * 25

            # Фон элемента
            item_rect = QGraphicsRectItem(self.x, item_y, width, 25)
            item_rect.setPen(QPen(QColor("#8e44ad"), 1))
            item_rect.setBrush(QBrush(QColor("#ecf0f1")))

            # Ключ
            key_str = str(key)
            if len(key_str) > 8:
                key_str = key_str[:6] + ".."

            key_text = QGraphicsTextItem(f"{key_str}:")
            key_text.setPos(self.x + 5, item_y + 3)
            key_text.setDefaultTextColor(QColor("#2c3e50"))
            key_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

            # Значение
            value_str = str(value)
            if len(value_str) > 8:
                value_str = value_str[:6] + ".."

            value_text = QGraphicsTextItem(value_str)
            value_text.setPos(self.x + 60, item_y + 3)
            value_text.setDefaultTextColor(QColor("#7f8c8d"))
            value_text.setFont(QFont("Arial", 8))

            self.scene.addItem(item_rect)
            self.scene.addItem(key_text)
            self.scene.addItem(value_text)
            self.elements.extend([item_rect, key_text, value_text])

    def create_simple_object(self):
        """Создание простого объекта"""
        width = 80
        height = 40

        # Фон объекта
        obj_rect = QGraphicsRectItem(self.x, self.y, width, height)
        obj_rect.setPen(QPen(QColor("#27ae60"), 2))
        obj_rect.setBrush(QBrush(QColor("#2ecc71")))

        # Значение
        value_str = str(self.content)
        if len(value_str) > 10:
            value_str = value_str[:8] + ".."

        value_text = QGraphicsTextItem(value_str)
        value_text.setPos(self.x + 5, self.y + 10)
        value_text.setDefaultTextColor(QColor("white"))
        value_text.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        self.scene.addItem(obj_rect)
        self.scene.addItem(value_text)
        self.elements.extend([obj_rect, value_text])

    def create_nested_object(self, obj_type: str, content: Any):
        """Создание объекта с вложенными структурами"""
        if obj_type == "list":
            self.create_nested_list()
        elif obj_type == "dict":
            self.create_nested_dict()

    def create_nested_list(self):
        """Создание списка с поддержкой вложенных элементов"""
        items = self.content if isinstance(self.content, list) else []
        visible_items = min(len(items), 4)  # Уменьшили для вложенных

        # Размеры
        cell_width = 50  # Увеличили для вложенных данных
        total_width = max(visible_items * cell_width, 120)
        height = 90  # Увеличили высоту

        # Заголовок объекта
        header_rect = QGraphicsRectItem(self.x, self.y, total_width, 20)
        header_rect.setPen(QPen(QColor("#c0392b"), 2))
        header_rect.setBrush(QBrush(QColor("#e74c3c")))

        header_text = QGraphicsTextItem(f"list (len={len(items)})")
        header_text.setPos(self.x + 5, self.y + 2)
        header_text.setDefaultTextColor(QColor("white"))
        header_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(header_text)
        self.elements.extend([header_rect, header_text])

        # Элементы списка
        for i in range(visible_items):
            cell_x = self.x + i * cell_width
            cell_y = self.y + 20

            # Ячейка
            cell_rect = QGraphicsRectItem(cell_x, cell_y, cell_width, 65)
            cell_rect.setPen(QPen(QColor("#c0392b"), 1))
            cell_rect.setBrush(QBrush(QColor("#ecf0f1")))

            # Индекс
            index_text = QGraphicsTextItem(str(i))
            index_text.setPos(cell_x + 2, cell_y + 2)
            index_text.setDefaultTextColor(QColor("#2c3e50"))
            index_text.setFont(QFont("Arial", 7))

            # Разделительная линия
            line_rect = QGraphicsRectItem(cell_x + 2, cell_y + 18, cell_width - 4, 1)
            line_rect.setBrush(QBrush(QColor("#bdc3c7")))

            # Значение с поддержкой вложенности
            value = items[i]
            if isinstance(value, (list, dict)):
                # Вложенная структура - создаем интерактивный индикатор
                if isinstance(value, list):
                    value_str = f"list[{len(value)}]"
                    value_color = QColor("#e74c3c")
                    indicator_color = QColor("#e74c3c")
                else:
                    value_str = f"dict[{len(value)}]"
                    value_color = QColor("#9b59b6")
                    indicator_color = QColor("#9b59b6")

                # Создаем интерактивный индикатор вместо простой точки
                indicator = HoverableNestedIndicator(
                    value,
                    cell_x + cell_width - 10,
                    cell_y + 45,
                    6, 6,
                    indicator_color,
                    self.scene
                )
                self.scene.addItem(indicator)
                self.elements.append(indicator)
            else:
                # Простое значение
                value_str = str(value)
                if len(value_str) > 6:
                    value_str = value_str[:5] + ".."
                value_color = QColor("#2c3e50")

            value_text = QGraphicsTextItem(value_str)
            value_text.setPos(cell_x + 2, cell_y + 22)
            value_text.setDefaultTextColor(value_color)
            value_text.setFont(QFont("Arial", 7))

            self.scene.addItem(cell_rect)
            self.scene.addItem(index_text)
            self.scene.addItem(line_rect)
            self.scene.addItem(value_text)
            self.elements.extend([cell_rect, index_text, line_rect, value_text])

        # Многоточие если нужно
        if len(items) > 4:
            dots_text = QGraphicsTextItem("...")
            dots_text.setPos(self.x + visible_items * cell_width + 5, self.y + 60)
            dots_text.setDefaultTextColor(QColor("#7f8c8d"))
            dots_text.setFont(QFont("Arial", 8))
            self.scene.addItem(dots_text)
            self.elements.append(dots_text)

    def create_nested_dict(self):
        """Создание словаря с поддержкой вложенных элементов"""
        items = self.content if isinstance(self.content, dict) else {}
        visible_items = min(len(items), 4)

        # Размеры
        width = 140  # Увеличили для вложенных данных
        height = 20 + visible_items * 30  # Увеличили высоту строк

        # Заголовок объекта
        header_rect = QGraphicsRectItem(self.x, self.y, width, 20)
        header_rect.setPen(QPen(QColor("#8e44ad"), 2))
        header_rect.setBrush(QBrush(QColor("#9b59b6")))

        header_text = QGraphicsTextItem(f"dict (len={len(items)})")
        header_text.setPos(self.x + 5, self.y + 2)
        header_text.setDefaultTextColor(QColor("white"))
        header_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(header_text)
        self.elements.extend([header_rect, header_text])

        # Элементы словаря
        for i, (key, value) in enumerate(list(items.items())[:visible_items]):
            item_y = self.y + 20 + i * 30

            # Фон элемента
            item_rect = QGraphicsRectItem(self.x, item_y, width, 30)
            item_rect.setPen(QPen(QColor("#8e44ad"), 1))
            item_rect.setBrush(QBrush(QColor("#ecf0f1")))

            # Ключ
            key_str = str(key)
            if len(key_str) > 8:
                key_str = key_str[:6] + ".."

            key_text = QGraphicsTextItem(f"{key_str}:")
            key_text.setPos(self.x + 5, item_y + 5)
            key_text.setDefaultTextColor(QColor("#2c3e50"))
            key_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

            # Значение с поддержкой вложенности
            if isinstance(value, (list, dict)):
                # Вложенная структура
                if isinstance(value, list):
                    value_str = f"list[{len(value)}]"
                    value_color = QColor("#e74c3c")
                    indicator_color = QColor("#e74c3c")
                else:
                    value_str = f"dict[{len(value)}]"
                    value_color = QColor("#9b59b6")
                    indicator_color = QColor("#9b59b6")

                # Создаем интерактивный индикатор
                indicator = HoverableNestedIndicator(
                    value,
                    self.x + width - 15,
                    item_y + 12,
                    6, 6,
                    indicator_color,
                    self.scene
                )
                self.scene.addItem(indicator)
                self.elements.append(indicator)
            else:
                # Простое значение
                value_str = str(value)
                if len(value_str) > 10:
                    value_str = value_str[:8] + ".."
                value_color = QColor("#7f8c8d")

            value_text = QGraphicsTextItem(value_str)
            value_text.setPos(self.x + 70, item_y + 5)
            value_text.setDefaultTextColor(value_color)
            value_text.setFont(QFont("Arial", 8))

            self.scene.addItem(item_rect)
            self.scene.addItem(key_text)
            self.scene.addItem(value_text)
            self.elements.extend([item_rect, key_text, value_text])

    def get_connection_point(self) -> Tuple[float, float]:
        """Получение точки для подключения стрелки"""
        return (self.x, self.y + 10)  # Левая сторона объекта

    def remove_from_scene(self):
        """Удаление объекта со сцены"""
        for element in self.elements:
            self.scene.removeItem(element)
        self.elements.clear()


class ArrowWidget:
    """Виджет стрелки между переменной и объектом"""

    def __init__(self, scene, start_point: Tuple[float, float], end_point: Tuple[float, float]):
        self.scene = scene
        self.start_point = start_point
        self.end_point = end_point
        self.elements = []

        self.create_arrow()

    def create_arrow(self):
        """Создание стрелки"""
        # Простая прямая стрелка
        path = QPainterPath()
        path.moveTo(self.start_point[0], self.start_point[1])
        path.lineTo(self.end_point[0], self.end_point[1])

        # Наконечник стрелки
        arrow_size = 6
        dx = self.end_point[0] - self.start_point[0]
        dy = self.end_point[1] - self.start_point[1]
        length = (dx * dx + dy * dy) ** 0.5

        if length > 0:
            dx /= length
            dy /= length

            # Точки наконечника
            p1_x = self.end_point[0] - arrow_size * dx + arrow_size * 0.5 * dy
            p1_y = self.end_point[1] - arrow_size * dy - arrow_size * 0.5 * dx
            p2_x = self.end_point[0] - arrow_size * dx - arrow_size * 0.5 * dy
            p2_y = self.end_point[1] - arrow_size * dy + arrow_size * 0.5 * dx

            path.lineTo(p1_x, p1_y)
            path.moveTo(self.end_point[0], self.end_point[1])
            path.lineTo(p2_x, p2_y)

        # Создаем графический элемент
        arrow_item = QGraphicsPathItem(path)
        arrow_item.setPen(QPen(QColor("#2c3e50"), 2))

        self.scene.addItem(arrow_item)
        self.elements.append(arrow_item)

    def remove_from_scene(self):
        """Удаление стрелки со сцены"""
        for element in self.elements:
            self.scene.removeItem(element)
        self.elements.clear()


class PythonTutorScene(QGraphicsScene):
    """Сцена визуализации в стиле Python Tutor"""

    def __init__(self):
        super().__init__()

        # Настройки сцены
        self.setSceneRect(0, 0, 800, 600)
        self.setBackgroundBrush(QBrush(QColor("#ffffff")))

        # Хранилища
        self.frames = {}
        self.objects = {}
        self.arrows = []

        # Позиции
        self.frame_start_x = 20
        self.frame_start_y = 50
        self.object_start_x = 400
        self.object_start_y = 50

        # Создаем заголовки секций
        self.create_section_headers()

    def create_section_headers(self):
        """Создание заголовков секций Frames и Objects"""
        # Заголовок Frames
        frames_header = QGraphicsTextItem("Frames")
        frames_header.setPos(self.frame_start_x, 20)
        frames_header.setDefaultTextColor(QColor("#2c3e50"))
        frames_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # Заголовок Objects
        objects_header = QGraphicsTextItem("Objects")
        objects_header.setPos(self.object_start_x, 20)
        objects_header.setDefaultTextColor(QColor("#2c3e50"))
        objects_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.addItem(frames_header)
        self.addItem(objects_header)

    def clear_all(self):
        """Очистка всех элементов"""
        # Удаляем фреймы
        for frame in self.frames.values():
            frame.remove_from_scene()
        self.frames.clear()

        # Удаляем объекты
        for obj in self.objects.values():
            obj.remove_from_scene()
        self.objects.clear()

        # Удаляем стрелки
        for arrow in self.arrows:
            arrow.remove_from_scene()
        self.arrows.clear()

    def update_visualization(self, variables: Dict[str, Any]):
        """Обновление визуализации"""
        self.clear_all()

        # Создаем глобальный фрейм
        global_frame = FrameWidget(self, "Global frame", self.frame_start_x, self.frame_start_y)
        self.frames["global"] = global_frame

        # Анализируем переменные
        complex_objects = {}
        object_counter = 0

        # Сначала обрабатываем все переменные
        for name, value in variables.items():
            # Проверяем, является ли значение функцией
            if callable(value) and hasattr(value, '__name__') and not isinstance(value, type):
                # Это пользовательская функция
                obj_id = f"obj_{object_counter}"
                complex_objects[obj_id] = {
                    'name': name,
                    'type': 'function',
                    'content': value,
                    'var_name': name
                }
                object_counter += 1

                # Добавляем переменную как ссылку
                connection_point = global_frame.add_variable(name, value, is_reference=True)
                complex_objects[obj_id]['connection_point'] = connection_point

            elif isinstance(value, (list, dict)):
                # Сложный объект - создаем ссылку
                obj_id = f"obj_{object_counter}"
                obj_type = 'list' if isinstance(value, list) else 'dict'
                complex_objects[obj_id] = {
                    'name': name,
                    'type': obj_type,
                    'content': value,
                    'var_name': name
                }
                object_counter += 1

                # Добавляем переменную как ссылку
                connection_point = global_frame.add_variable(name, value, is_reference=True)
                complex_objects[obj_id]['connection_point'] = connection_point

            elif hasattr(value, '__dict__') and not isinstance(value, (int, float, str, bool, type(None), type)):
                # Пользовательский объект (экземпляр класса)
                obj_id = f"obj_{object_counter}"
                complex_objects[obj_id] = {
                    'name': name,
                    'type': 'class_instance',
                    'content': value,
                    'var_name': name
                }
                object_counter += 1

                # Добавляем переменную как ссылку
                connection_point = global_frame.add_variable(name, value, is_reference=True)
                complex_objects[obj_id]['connection_point'] = connection_point
            else:
                # Простая переменная - отображаем значение
                global_frame.add_variable(name, value, is_reference=False)

        # Теперь создаем объекты и стрелки
        for obj_id, obj_info in complex_objects.items():
            obj_y = self.object_start_y + len(self.objects) * 120

            if obj_info['type'] == 'function':
                # Создаем виджет для функции
                obj_widget = FunctionWidget(
                    self, obj_id,
                    obj_info['content'],
                    self.object_start_x, obj_y
                )
            elif obj_info['type'] == 'class_instance':
                obj_widget = ObjectWidget(
                    self, obj_id,
                    obj_info['type'],
                    obj_info['content'],
                    self.object_start_x, obj_y
                )
            else:
                # Обычные объекты
                obj_widget = ObjectWidget(
                    self, obj_id,
                    obj_info['type'],
                    obj_info['content'],
                    self.object_start_x, obj_y
                )

            self.objects[obj_id] = obj_widget

            # Создаем стрелку если есть точка подключения
            connection_point = obj_info['connection_point']
            if connection_point and connection_point[0] > 0:
                if obj_info['type'] == 'class_instance':
                    target_point = obj_widget.class_widget.get_connection_point()
                else:
                    target_point = obj_widget.get_connection_point()

                arrow = ArrowWidget(self, connection_point, target_point)
                self.arrows.append(arrow)


class NestedStructureTooltip(QGraphicsRectItem):
    """Всплывающее окно для отображения содержимого вложенных структур"""

    def __init__(self, content: Any, x: float, y: float, parent_scene):
        self.content = content
        self.parent_scene = parent_scene
        self.elements = []

        # Простой расчет размеров
        if isinstance(content, list):
            width = 250
            height = 120
        elif isinstance(content, dict):
            width = 280
            height = 40 + len(content) * 25  # 25px на строку
            height = min(height, 200)  # Максимум 200px
        else:
            width = 180
            height = 80

        super().__init__(x, y, width, height)

        # Простой и чистый дизайн
        self.setPen(QPen(QColor("#34495e"), 2))
        self.setBrush(QBrush(QColor("#ffffff")))
        self.setZValue(1000)

        # Простая тень
        shadow = QGraphicsRectItem(x + 3, y + 3, width, height)
        shadow.setPen(QPen(Qt.PenStyle.NoPen))
        shadow.setBrush(QBrush(QColor("#bdc3c7")))
        shadow.setOpacity(0.4)
        shadow.setZValue(999)

        parent_scene.addItem(shadow)
        parent_scene.addItem(self)
        self.elements.append(shadow)

        self.create_content()

    def create_content(self):
        """Создание содержимого"""
        if isinstance(self.content, list):
            self.create_simple_list()
        elif isinstance(self.content, dict):
            self.create_simple_dict()
        else:
            self.create_simple_value()

    def create_simple_list(self):
        """Простое отображение списка"""
        # Заголовок
        title = QGraphicsTextItem(f"list (длина: {len(self.content)})", self)
        title.setPos(10, 10)
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setDefaultTextColor(QColor("#e74c3c"))

        # Показываем первые 5 элементов
        y_offset = 35
        for i, item in enumerate(self.content[:5]):
            # Фон строки
            if i % 2 == 0:
                row_bg = QGraphicsRectItem(5, y_offset - 2, self.rect().width() - 10, 20, self)
                row_bg.setBrush(QBrush(QColor("#f8f9fa")))
                row_bg.setPen(QPen(Qt.PenStyle.NoPen))

            # Индекс и значение
            text = f"[{i}] = {str(item)[:20]}{'...' if len(str(item)) > 20 else ''}"
            item_text = QGraphicsTextItem(text, self)
            item_text.setPos(10, y_offset)
            item_text.setFont(QFont("Arial", 9))
            item_text.setDefaultTextColor(QColor("#2c3e50"))

            y_offset += 18

        # Многоточие если элементов больше
        if len(self.content) > 5:
            more_text = QGraphicsTextItem(f"... и еще {len(self.content) - 5} элементов", self)
            more_text.setPos(10, y_offset)
            more_text.setFont(QFont("Arial", 9))
            more_text.setDefaultTextColor(QColor("#7f8c8d"))

    def create_simple_dict(self):
        """Простое отображение словаря"""
        # Заголовок
        title = QGraphicsTextItem(f"dict (ключей: {len(self.content)})", self)
        title.setPos(10, 10)
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setDefaultTextColor(QColor("#9b59b6"))

        # Показываем первые 6 пар ключ-значение
        y_offset = 35
        for i, (key, value) in enumerate(list(self.content.items())[:6]):
            # Фон строки
            if i % 2 == 0:
                row_bg = QGraphicsRectItem(5, y_offset - 2, self.rect().width() - 10, 22, self)
                row_bg.setBrush(QBrush(QColor("#f8f9fa")))
                row_bg.setPen(QPen(Qt.PenStyle.NoPen))

            # Ключ и значение
            key_str = str(key)[:15] + ('...' if len(str(key)) > 15 else '')
            value_str = str(value)[:20] + ('...' if len(str(value)) > 20 else '')
            text = f"{key_str}: {value_str}"

            item_text = QGraphicsTextItem(text, self)
            item_text.setPos(10, y_offset)
            item_text.setFont(QFont("Arial", 9))
            item_text.setDefaultTextColor(QColor("#2c3e50"))

            y_offset += 22

        # Многоточие если пар больше
        if len(self.content) > 6:
            more_text = QGraphicsTextItem(f"... и еще {len(self.content) - 6} пар", self)
            more_text.setPos(10, y_offset)
            more_text.setFont(QFont("Arial", 9))
            more_text.setDefaultTextColor(QColor("#7f8c8d"))

    def create_simple_value(self):
        """Простое отображение значения"""
        value_str = str(self.content)
        if len(value_str) > 30:
            value_str = value_str[:27] + "..."

        text = QGraphicsTextItem(value_str, self)
        text.setPos(10, 25)
        text.setFont(QFont("Arial", 12))
        text.setDefaultTextColor(QColor("#2c3e50"))

    def remove_from_scene(self):
        """Удаление всплывающего окна"""
        for element in self.elements:
            if element.scene():
                element.scene().removeItem(element)
        if self.scene():
            self.scene().removeItem(self)


class HoverableNestedIndicator(QGraphicsRectItem):
    """Интерактивный индикатор вложенной структуры"""

    def __init__(self, content: Any, x: float, y: float, width: float, height: float, color: QColor, parent_scene):
        super().__init__(x, y, width, height)
        self.content = content
        self.parent_scene = parent_scene
        self.tooltip = None

        # Настройка внешнего вида
        self.setPen(QPen(color, 2))
        self.setBrush(QBrush(color))

        # КЛЮЧЕВЫЕ НАСТРОЙКИ для работы hover событий
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

        # Курсор указателя
        from PyQt6.QtCore import Qt
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Устанавливаем Z-значение выше других элементов
        self.setZValue(100)

    def hoverEnterEvent(self, event):
        """Событие наведения мыши"""
        print(f"DEBUG: Hover enter на {type(self.content).__name__}")

        # Улучшенное позиционирование - правее и ниже
        tooltip_x = self.x()   # Увеличили отступ вправо
        tooltip_y = self.y() + 10  # Сдвинули вниз вместо вверх

        # Проверяем границы сцены и корректируем позицию
        scene_rect = self.parent_scene.sceneRect()

        # Если окно выходит за правую границу, показываем слева
        if tooltip_x + 280 > scene_rect.width():
            tooltip_x = self.x() - 290

        # Если окно выходит за нижнюю границу, показываем выше
        if tooltip_y + 200 > scene_rect.height():
            tooltip_y = self.y() - 220

        self.tooltip = NestedStructureTooltip(
            self.content,
            tooltip_x,
            tooltip_y,
            self.parent_scene
        )

        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Событие ухода мыши"""
        print(f"DEBUG: Hover leave на {type(self.content).__name__}")  # Отладка

        # Удаляем всплывающее окно
        if self.tooltip:
            self.tooltip.remove_from_scene()
            self.tooltip = None

        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """Обработка клика мыши (альтернатива hover)"""
        print(f"DEBUG: Click на {type(self.content).__name__}")

        # Если hover не работает, показываем tooltip по клику
        if not self.tooltip:
            self.hoverEnterEvent(event)
        else:
            self.hoverLeaveEvent(event)

        super().mousePressEvent(event)


class ClassInstanceWidget:
    """Виджет для отображения экземпляра класса"""

    def __init__(self, scene, obj_id: str, instance: Any, class_name: str, x: float, y: float):
        self.scene = scene
        self.obj_id = obj_id
        self.instance = instance
        self.class_name = class_name
        self.elements = []
        self.x = x
        self.y = y

        # Получаем атрибуты объекта
        self.attributes = self._get_instance_attributes()

        self.create_class_instance()

    def _get_instance_attributes(self) -> Dict[str, Any]:
        """Получение атрибутов экземпляра класса"""
        attributes = {}
        try:
            # Получаем все атрибуты, которые не являются методами
            for attr_name in dir(self.instance):
                if not attr_name.startswith('_'):  # Игнорируем приватные атрибуты
                    attr_value = getattr(self.instance, attr_name)
                    # Игнорируем методы
                    if not callable(attr_value):
                        attributes[attr_name] = attr_value
        except:
            pass
        return attributes

    def create_class_instance(self):
        """Создание виджета экземпляра класса"""
        # Размеры виджета
        visible_attrs = min(len(self.attributes), 5)
        width = 160
        height = 40 + visible_attrs * 25  # 25px на атрибут

        # Заголовок объекта
        header_rect = QGraphicsRectItem(self.x, self.y, width, 25)
        header_rect.setPen(QPen(QColor("#27ae60"), 2))
        header_rect.setBrush(QBrush(QColor("#2ecc71")))

        header_text = QGraphicsTextItem(f"{self.class_name} instance")
        header_text.setPos(self.x + 5, self.y + 3)
        header_text.setDefaultTextColor(QColor("white"))
        header_text.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(header_text)
        self.elements.extend([header_rect, header_text])

        # Атрибуты объекта
        for i, (attr_name, attr_value) in enumerate(list(self.attributes.items())[:visible_attrs]):
            attr_y = self.y + 25 + i * 25

            # Фон атрибута
            attr_rect = QGraphicsRectItem(self.x, attr_y, width, 25)
            attr_rect.setPen(QPen(QColor("#27ae60"), 1))
            attr_rect.setBrush(QBrush(QColor("#d5f4e6")))

            # Имя атрибута
            attr_name_text = QGraphicsTextItem(f"{attr_name}:")
            attr_name_text.setPos(self.x + 5, attr_y + 3)
            attr_name_text.setDefaultTextColor(QColor("#2c3e50"))
            attr_name_text.setFont(QFont("Arial", 8, QFont.Weight.Bold))

            # Значение атрибута
            if isinstance(attr_value, (list, dict)):
                # Сложный атрибут - показываем тип
                if isinstance(attr_value, list):
                    value_str = f"list[{len(attr_value)}]"
                    value_color = QColor("#e74c3c")
                else:
                    value_str = f"dict[{len(attr_value)}]"
                    value_color = QColor("#9b59b6")

                # Добавляем точку для стрелки
                dot = QGraphicsRectItem(self.x + width - 15, attr_y + 10, 6, 6)
                dot.setPen(QPen(value_color, 2))
                dot.setBrush(QBrush(value_color))
                self.scene.addItem(dot)
                self.elements.append(dot)
            else:
                # Простое значение
                value_str = str(attr_value)
                if len(value_str) > 12:
                    value_str = value_str[:10] + ".."
                value_color = QColor("#7f8c8d")

            value_text = QGraphicsTextItem(value_str)
            value_text.setPos(self.x + 80, attr_y + 3)
            value_text.setDefaultTextColor(value_color)
            value_text.setFont(QFont("Arial", 8))

            self.scene.addItem(attr_rect)
            self.scene.addItem(attr_name_text)
            self.scene.addItem(value_text)
            self.elements.extend([attr_rect, attr_name_text, value_text])

        # Многоточие если атрибутов больше
        if len(self.attributes) > 5:
            dots_text = QGraphicsTextItem("...")
            dots_text.setPos(self.x + 5, self.y + 25 + visible_attrs * 25)
            dots_text.setDefaultTextColor(QColor("#7f8c8d"))
            dots_text.setFont(QFont("Arial", 8))
            self.scene.addItem(dots_text)
            self.elements.append(dots_text)

    def get_connection_point(self) -> Tuple[float, float]:
        """Получение точки для подключения стрелки"""
        return (self.x, self.y + 12)

    def remove_from_scene(self):
        """Удаление объекта со сцены"""
        for element in self.elements:
            self.scene.removeItem(element)
        self.elements.clear()


class ClassDefinitionWidget:
    """Виджет для отображения определения класса"""

    def __init__(self, scene, obj_id: str, class_obj: type, x: float, y: float):
        self.scene = scene
        self.obj_id = obj_id
        self.class_obj = class_obj
        self.class_name = class_obj.__name__
        self.elements = []
        self.x = x
        self.y = y

        # Получаем методы класса
        self.methods = self._get_class_methods()

        self.create_class_definition()

    def _get_class_methods(self) -> List[str]:
        """Получение методов класса"""
        methods = []
        try:
            for attr_name in dir(self.class_obj):
                if not attr_name.startswith('_') or attr_name == '__init__':
                    attr_value = getattr(self.class_obj, attr_name)
                    if callable(attr_value):
                        methods.append(attr_name)
        except:
            pass
        return methods

    def create_class_definition(self):
        """Создание виджета определения класса"""
        # Размеры виджета
        visible_methods = min(len(self.methods), 3)
        width = 160
        height = 40 + visible_methods * 25

        # Заголовок класса
        header_rect = QGraphicsRectItem(self.x, self.y, width, 25)
        header_rect.setPen(QPen(QColor("#f39c12"), 2))
        header_rect.setBrush(QBrush(QColor("#f1c40f")))

        header_text = QGraphicsTextItem(f"{self.class_name} class")
        header_text.setPos(self.x + 5, self.y + 3)
        header_text.setDefaultTextColor(QColor("#2c3e50"))
        header_text.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(header_text)
        self.elements.extend([header_rect, header_text])

        # Методы класса
        for i, method_name in enumerate(self.methods[:visible_methods]):
            method_y = self.y + 25 + i * 25

            # Фон метода
            method_rect = QGraphicsRectItem(self.x, method_y, width, 25)
            method_rect.setPen(QPen(QColor("#f39c12"), 1))
            method_rect.setBrush(QBrush(QColor("#fef9e7")))

            # Имя метода
            method_text = QGraphicsTextItem(f"function {method_name}")
            method_text.setPos(self.x + 5, method_y + 3)
            method_text.setDefaultTextColor(QColor("#2c3e50"))
            method_text.setFont(QFont("Arial", 8))

            self.scene.addItem(method_rect)
            self.scene.addItem(method_text)
            self.elements.extend([method_rect, method_text])

        # Многоточие если методов больше
        if len(self.methods) > 3:
            dots_text = QGraphicsTextItem("...")
            dots_text.setPos(self.x + 5, self.y + 25 + visible_methods * 25)
            dots_text.setDefaultTextColor(QColor("#7f8c8d"))
            dots_text.setFont(QFont("Arial", 8))
            self.scene.addItem(dots_text)
            self.elements.append(dots_text)

    def get_connection_point(self) -> Tuple[float, float]:
        """Получение точки для подключения стрелки"""
        return (self.x, self.y + 12)

    def remove_from_scene(self):
        """Удаление объекта со сцены"""
        for element in self.elements:
            self.scene.removeItem(element)
        self.elements.clear()


class FunctionWidget:
    """Виджет для отображения функции"""

    def __init__(self, scene, obj_id: str, func_obj: Any, x: float, y: float):
        self.scene = scene
        self.obj_id = obj_id
        self.func_obj = func_obj
        self.func_name = getattr(func_obj, '__name__', 'function')
        self.elements = []
        self.x = x
        self.y = y

        self.create_function_widget()

    def create_function_widget(self):
        """Создание виджета функции"""
        width = 140
        height = 50

        # Заголовок функции
        header_rect = QGraphicsRectItem(self.x, self.y, width, height)
        header_rect.setPen(QPen(QColor("#8e44ad"), 2))
        header_rect.setBrush(QBrush(QColor("#9b59b6")))

        # Название функции
        func_text = QGraphicsTextItem(f"function")
        func_text.setPos(self.x + 5, self.y + 5)
        func_text.setDefaultTextColor(QColor("white"))
        func_text.setFont(QFont("Arial", 8))

        name_text = QGraphicsTextItem(f"{self.func_name}")
        name_text.setPos(self.x + 5, self.y + 20)
        name_text.setDefaultTextColor(QColor("white"))
        name_text.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.scene.addItem(header_rect)
        self.scene.addItem(func_text)
        self.scene.addItem(name_text)
        self.elements.extend([header_rect, func_text, name_text])

    def get_connection_point(self) -> Tuple[float, float]:
        """Получение точки для подключения стрелки"""
        return (self.x, self.y + 25)

    def remove_from_scene(self):
        """Удаление объекта со сцены"""
        for element in self.elements:
            self.scene.removeItem(element)
        self.elements.clear()


