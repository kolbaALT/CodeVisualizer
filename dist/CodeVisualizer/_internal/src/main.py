import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    """Главная функция запуска приложения"""
    # Создаем приложение Qt
    app = QApplication(sys.argv)

    # Создаем главное окно
    window = MainWindow()

    # Показываем окно
    window.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
