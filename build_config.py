"""
Конфигурация для сборки приложения
"""

import os
import sys

# Информация о приложении
APP_NAME = "CodeVisualizer"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Визуализатор выполнения кода Python"
APP_AUTHOR = "Igor Kolbeshkin"
APP_COPYRIGHT = "Copyright © 2025"

# Пути
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")

# Настройки PyInstaller
PYINSTALLER_OPTIONS = {
    "name": APP_NAME,
    "onefile": False,  # Создаем папку с файлами для лучшей производительности
    "windowed": True,  # Без консоли
    "icon": "assets/icon.ico",  # Иконка приложения
    "add_data": [
        ("assets/*", "assets"),  # Копируем ресурсы
    ],
    "hidden_imports": [
        "PyQt6.QtSvg",
        "PyQt6.Qsci",
    ],
    "excludes": [
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
    ]
}

# Настройки для разных платформ
PLATFORM_CONFIGS = {
    "windows": {
        "installer_tool": "inno_setup",
        "executable_name": f"{APP_NAME}.exe",
        "installer_name": f"{APP_NAME}_Setup_v{APP_VERSION}.exe"
    },
    "macos": {
        "installer_tool": "create_dmg",
        "executable_name": f"{APP_NAME}.app",
        "installer_name": f"{APP_NAME}_v{APP_VERSION}.dmg"
    },
    "linux": {
        "installer_tool": "appimage",
        "executable_name": APP_NAME,
        "installer_name": f"{APP_NAME}_v{APP_VERSION}.AppImage"
    }
}
