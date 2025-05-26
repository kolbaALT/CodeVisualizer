"""
Скрипт для сборки приложения на разных платформах
"""

import os
import sys
import platform
import subprocess
import shutil
from build_config import *


def detect_platform():
    """Определение текущей платформы"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        raise Exception(f"Неподдерживаемая платформа: {system}")


def clean_build_dirs():
    """Очистка директорий сборки"""
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Очищена директория: {dir_path}")


def build_executable():
    """Сборка исполняемого файла с PyInstaller"""
    print("Сборка исполняемого файла...")

    # Формируем команду PyInstaller
    cmd = [
        "pyinstaller",
        "--name", PYINSTALLER_OPTIONS["name"],
        "--windowed" if PYINSTALLER_OPTIONS["windowed"] else "--console",
        "--distpath", DIST_DIR,
        "--workpath", BUILD_DIR,
    ]

    # Добавляем иконку если есть
    if os.path.exists(PYINSTALLER_OPTIONS["icon"]):
        cmd.extend(["--icon", PYINSTALLER_OPTIONS["icon"]])

    # Добавляем данные
    for src, dst in PYINSTALLER_OPTIONS["add_data"]:
        cmd.extend(["--add-data", f"{src};{dst}"])

    # Добавляем скрытые импорты
    for module in PYINSTALLER_OPTIONS["hidden_imports"]:
        cmd.extend(["--hidden-import", module])

    # Исключаем ненужные модули
    for module in PYINSTALLER_OPTIONS["excludes"]:
        cmd.extend(["--exclude-module", module])

    # Главный файл
    cmd.append("src/main.py")

    # Запускаем сборку
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Исполняемый файл собран успешно!")
        return True
    else:
        print("❌ Ошибка при сборке:")
        print(result.stderr)
        return False


def create_windows_installer():
    """Создание установщика для Windows"""
    print("Создание установщика для Windows...")

    # Создаем скрипт Inno Setup
    iss_content = f"""
[Setup]
AppName={APP_NAME}
AppVersion={APP_VERSION}
AppPublisher={APP_AUTHOR}
DefaultDirName={{pf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
OutputDir={DIST_DIR}
OutputBaseFilename={PLATFORM_CONFIGS['windows']['installer_name'].replace('.exe', '')}
Compression=lzma
SolidCompression=yes

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "{DIST_DIR}\\{APP_NAME}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"
Name: "{{commondesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{APP_NAME}.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{APP_NAME}.exe"; Description: "{{cm:LaunchProgram,{APP_NAME}}}"; Flags: nowait postinstall skipifsilent
"""

    # Сохраняем скрипт
    iss_file = os.path.join(PROJECT_ROOT, f"{APP_NAME}.iss")
    with open(iss_file, "w", encoding="utf-8") as f:
        f.write(iss_content)

    print(f"Скрипт Inno Setup создан: {iss_file}")
    print("Для создания установщика запустите:")
    print(f"iscc {iss_file}")


def create_macos_installer():
    """Создание установщика для macOS"""
    print("Создание DMG для macOS...")
    print("Для создания DMG используйте:")
    print(
        f"create-dmg --volname '{APP_NAME}' --window-pos 200 120 --window-size 600 300 --icon-size 100 --icon '{APP_NAME}.app' 175 120 --hide-extension '{APP_NAME}.app' --app-drop-link 425 120 '{PLATFORM_CONFIGS['macos']['installer_name']}' '{DIST_DIR}/{APP_NAME}.app'")


def create_linux_installer():
    """Создание AppImage для Linux"""
    print("Создание AppImage для Linux...")
    print("Для создания AppImage используйте:")
    print(f"appimagetool {DIST_DIR}/{APP_NAME} {DIST_DIR}/{PLATFORM_CONFIGS['linux']['installer_name']}")


def main():
    """Главная функция сборки"""
    current_platform = detect_platform()
    print(f"Сборка для платформы: {current_platform}")

    # Очищаем старые сборки
    clean_build_dirs()

    # Собираем исполняемый файл
    if not build_executable():
        return False

    # Создаем установщик для текущей платформы
    if current_platform == "windows":
        create_windows_installer()
    elif current_platform == "macos":
        create_macos_installer()
    elif current_platform == "linux":
        create_linux_installer()

    print(f"✅ Сборка для {current_platform} завершена!")
    print(f"Файлы находятся в: {DIST_DIR}")

    return True


if __name__ == "__main__":
    main()
