@echo off
chcp 65001 >nul
title Vetlan Trading Bot
color 0A

REM Переход в директорию скрипта
cd /d "%~dp0"

echo ========================================
echo    Vetlan Trading Bot
echo ========================================
echo.
echo [*] Запуск стратегии...
echo [*] Для остановки нажмите Ctrl+C
echo.
echo ========================================
echo.

python run_strategy.py

if errorlevel 1 (
    echo.
    echo [!] Ошибка при запуске бота
    echo [!] Убедитесь, что зависимости установлены:
    echo [!] pip install -r requirements.txt
)

echo.
echo ========================================
echo [*] Бот остановлен
echo ========================================
pause
