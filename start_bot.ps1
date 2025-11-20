# Vetlan Trading Bot Launcher (PowerShell)
# Запуск: двойной клик по файлу или правый клик -> "Выполнить с PowerShell"

$Host.UI.RawUI.WindowTitle = "Vetlan Trading Bot"

# Переход в директорию скрипта
Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Green
Write-Host "   Vetlan Trading Bot" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Определение пути к Python
$pythonPath = $null

if (Test-Path "venv\Scripts\python.exe") {
    $pythonPath = "venv\Scripts\python.exe"
    Write-Host "[*] Использование Python из виртуального окружения..." -ForegroundColor Yellow
} elseif (Test-Path "venv\bin\python.exe") {
    $pythonPath = "venv\bin\python.exe"
    Write-Host "[*] Использование Python из виртуального окружения..." -ForegroundColor Yellow
} else {
    $pythonPath = "python"
    Write-Host "[!] Виртуальное окружение не найдено" -ForegroundColor Red
    Write-Host "[!] Попытка использовать системный Python..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[*] Запуск стратегии..." -ForegroundColor Yellow
Write-Host "[*] Для остановки нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

try {
    & $pythonPath run_strategy.py
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne $null) {
        Write-Host ""
        Write-Host "[!] Ошибка при запуске бота (код: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "[!] Проверьте, что виртуальное окружение создано и зависимости установлены" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "[!] Ошибка при запуске: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "[*] Бот остановлен" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

