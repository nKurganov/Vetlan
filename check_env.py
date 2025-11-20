"""
Проверка переменных окружения перед запуском бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    "BYBIT_API_KEY",
    "BYBIT_API_SECRET",
    "BYBIT_ENV",
]

optional_vars = [
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
]

def check_environment():
    """Проверяет наличие необходимых переменных окружения"""
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ ОШИБКА: Отсутствуют обязательные переменные окружения:")
        for var in missing:
            print(f"   - {var}")
        print("\nУстановите их через:")
        print("  - Локально: создайте файл .env")
        print("  - На сервере: настройте Environment Variables")
        return False
    
    print("✅ Все обязательные переменные окружения установлены")
    
    # Проверка опциональных
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print("⚠️  ВНИМАНИЕ: Отсутствуют опциональные переменные:")
        for var in missing_optional:
            print(f"   - {var}")
        print("   Telegram уведомления будут отключены")
    
    # Показываем окружение (без секретов)
    env = os.getenv("BYBIT_ENV", "testnet")
    print(f"\n📊 Окружение: {env.upper()}")
    print(f"🔑 API Key: {'✅ Установлен' if os.getenv('BYBIT_API_KEY') else '❌ Отсутствует'}")
    print(f"🔐 API Secret: {'✅ Установлен' if os.getenv('BYBIT_API_SECRET') else '❌ Отсутствует'}")
    
    return True

if __name__ == "__main__":
    if check_environment():
        print("\n✅ Окружение готово к запуску бота")
        exit(0)
    else:
        print("\n❌ Исправьте ошибки перед запуском")
        exit(1)

