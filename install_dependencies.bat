@echo off
chcp 65001 >nul
title Установка зависимостей
color 0B

echo ========================================
echo    Установка зависимостей Vetlan Bot
echo ========================================
echo.

REM Переход в директорию скрипта
cd /d "%~dp0"

echo [*] Установка зависимостей из requirements.txt...
echo.

if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo [!] Файл requirements.txt не найден
    echo [*] Установка базовых зависимостей...
    pip install pybit pandas ta python-dotenv colorama requests
)

if errorlevel 1 (
    echo.
    echo [!] Ошибка при установке зависимостей
    pause
    exit /b 1
)

echo.
echo ========================================
echo [*] Зависимости установлены успешно!
echo ========================================
echo.
pause

