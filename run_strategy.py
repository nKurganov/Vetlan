import time
import logging
from exchange.bybit_client import BybitClient
from strategy.strategy import Strategy
from orders.order_manager import OrderManager
from utils.notifier import TelegramNotifier
from utils.stats_logger import StatsLogger
from config.bybit_config import BYBIT_CONFIG


logger = logging.getLogger("vetlan_strategy")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    logger.addHandler(handler)


def print_config_summary(config):
    """
    Выводит сводку ключевых настроек бота перед запуском.
    """
    print("\n" + "=" * 60)
    print(" " * 15 + "НАСТРОЙКИ БОТА")
    print("=" * 60)
    
    # Окружение и подключение
    env = config.get("environment", "testnet").upper()
    env_icon = "🔴" if env == "MAINNET" else "🟡"
    print(f"\n{env_icon} Окружение: {env}")
    print(f"📊 Таймфрейм: {config.get('interval', '15')} минут")
    print(f"📈 Монет в мониторинге: {len(config.get('coins', []))}")
    
    # Торговые настройки
    print(f"\n💹 ТОРГОВЛЯ:")
    long_status = "✅ ВКЛ" if config.get("enable_long", False) else "❌ ВЫКЛ"
    short_status = "✅ ВКЛ" if config.get("enable_short", False) else "❌ ВЫКЛ"
    print(f"   LONG:  {long_status}")
    print(f"   SHORT: {short_status}")
    
    # Индикаторы
    print(f"\n📊 ИНДИКАТОРЫ:")
    print(f"   RSI период: {config.get('rsi_period', 14)}")
    print(f"   RSI LONG:  < {config.get('rsi_buy', 25)}")
    print(f"   RSI SHORT: > {config.get('rsi_sell', 70)}")
    print(f"   EMA период: {config.get('ema_period', 50)}")
    print(f"   ATR период: {config.get('atr_period', 14)}")
    
    # Фильтры
    print(f"\n🔍 ФИЛЬТРЫ:")
    patterns = "✅ ВКЛ" if config.get("enable_patterns", False) else "❌ ВЫКЛ"
    trend = "✅ ВКЛ" if config.get("use_trend_filter", False) else "❌ ВЫКЛ"
    print(f"   Паттерны свечей: {patterns}")
    print(f"   Фильтр тренда (EMA): {trend}")
    print(f"   Мин. волатильность: {config.get('min_atr_pct', 0.3)}%")
    print(f"   Множитель объёма: {config.get('volume_mult', 1.5)}x")
    
    # Риск-менеджмент
    print(f"\n💰 РИСК-МЕНЕДЖМЕНТ:")
    print(f"   Риск на сделку: {config.get('risk_pct', 2)}%")
    print(f"   Мин. размер ордера: {config.get('min_order_usdt', 5)} USDT")
    print(f"   Макс. размер позиции: {config.get('max_position_pct', 10)}%")
    
    # TP/SL
    print(f"\n🎯 TAKE PROFIT / STOP LOSS:")
    tp_sl_status = "✅ ВКЛ" if config.get("enable_tp_sl", False) else "❌ ВЫКЛ"
    print(f"   Авто TP/SL: {tp_sl_status}")
    if config.get("enable_tp_sl", False):
        print(f"   LONG:  TP={config.get('tp_long_atr', 2.5)}x ATR, SL={config.get('sl_long_atr', 1.2)}x ATR")
        print(f"   SHORT: TP={config.get('tp_short_atr', 2.5)}x ATR, SL={config.get('sl_short_atr', 1.2)}x ATR")
        print(f"   Мин. TP: {config.get('min_tp_pct', 0.01)*100}%")
        print(f"   Мин. SL: {config.get('min_sl_pct', 0.01)*100}%")
    
    # Уведомления
    telegram_token = config.get("telegram_token")
    telegram_chat = config.get("telegram_chat_id")
    telegram_status = "✅ ВКЛ" if (telegram_token and telegram_chat) else "❌ ВЫКЛ"
    print(f"\n📱 УВЕДОМЛЕНИЯ:")
    print(f"   Telegram: {telegram_status}")
    
    print("=" * 60 + "\n")


def format_positions_report(positions):
    if not positions:
        return "Открытых позиций нет."

    lines = ["Открытые позиции:"]
    for pos in positions:
        lines.append(
            "- {symbol}: размер {size:.4f}, вход {entry:.4f}".format(
                symbol=pos["symbol"],
                size=pos["size"],
                entry=pos["entryPrice"],
            )
        )
    return "\n".join(lines)


def run_strategy(poll_interval: int = 30):
    """
    Запускает основной цикл проверки сигналов по списку монет.
    """
    client = BybitClient(BYBIT_CONFIG)

    notifier = TelegramNotifier(
        BYBIT_CONFIG.get("telegram_token"),
        BYBIT_CONFIG.get("telegram_chat_id"),
    )

    orders = OrderManager(
        client=client.client,
        cfg=BYBIT_CONFIG,
        notifier=notifier,
    )

    strategy = Strategy(
        client=client.client,
        orders=orders,
        settings=BYBIT_CONFIG,
    )

    stats_logger = StatsLogger()

    coins = BYBIT_CONFIG["coins"]
    
    # ВЫВОД НАСТРОЕК ПЕРЕД ЗАПУСКОМ
    print_config_summary(BYBIT_CONFIG)
    
    logger.info("Запущена стратегия. Монеты: %s", ", ".join(coins))

    tracked_positions = {}
    initial_positions = orders.list_open_positions(coins)
    for pos in initial_positions:
        tracked_positions[pos["symbol"]] = pos

    # Получаем баланс для вывода
    balance = orders.get_usdt_balance()
    print(f"💰 Баланс: {balance:.2f} USDT")
    print(f"📊 Открытых позиций: {len(initial_positions)}")
    if initial_positions:
        print("   Открытые позиции:")
        for pos in initial_positions:
            print(f"   - {pos['symbol']}: {pos['size']:.4f} @ {pos['entryPrice']:.4f}")
    print(f"\n⏱️  Интервал проверки: {poll_interval} секунд")
    print("🚀 Бот запущен. Ожидание сигналов...\n")
    print("-" * 60 + "\n")

    if notifier:
        notifier.send(
            "🤖 Бот запущен\n"
            f"Баланс: {balance:.2f} USDT\n"
            f"{format_positions_report(initial_positions)}"
        )

    try:
        while True:
            for symbol in coins:
                prev_position = tracked_positions.get(symbol)
                current_position = orders.refresh_position(symbol)

                if current_position:
                    if current_position.get("pending"):
                        tracked_positions[symbol] = {"pending": True}
                        continue

                    tracked_positions[symbol] = {
                        "symbol": symbol,
                        "size": float(current_position.get("size", 0)),
                        "entryPrice": float(current_position.get("entryPrice", 0)),
                    }
                elif prev_position:
                    if prev_position.get("pending"):
                        tracked_positions.pop(symbol, None)
                    else:
                        # Позиция закрыта - логируем
                        entry_price = prev_position.get("entryPrice", 0)
                        size = prev_position.get("size", 0)
                        
                        # Получаем текущую цену как цену выхода
                        try:
                            klines_resp = client.client.get_kline(
                                category="linear",
                                symbol=symbol,
                                interval="1",
                                limit=1
                            )
                            if klines_resp.get("retCode") == 0:
                                klines = klines_resp.get("result", {}).get("list", [])
                                if klines:
                                    exit_price = float(klines[0][4])  # close price
                                    
                                    # Определяем направление позиции (нужно получить из истории или использовать сигнал)
                                    # Для упрощения используем разницу цен
                                    direction = "long" if exit_price > entry_price else "short"
                                    
                                    # Расчёт PnL
                                    if direction == "long":
                                        pnl = (exit_price - entry_price) * size
                                    else:
                                        pnl = (entry_price - exit_price) * size
                                    
                                    roi = (pnl / (entry_price * size)) * 100 if entry_price * size > 0 else 0
                                    
                                    stats_logger.log_trade(
                                        symbol=symbol,
                                        direction=direction,
                                        entry=entry_price,
                                        tp=0,  # Не знаем TP/SL при закрытии
                                        sl=0,
                                        exit_price=exit_price,
                                        pnl=pnl,
                                        roi=roi,
                                    )
                        except Exception as e:
                            logger.warning("[%s] Ошибка при логировании закрытия: %s", symbol, e)
                        
                        tracked_positions.pop(symbol, None)
                        if notifier:
                            notifier.send(
                                "📤 Позиция закрыта\n"
                                f"Символ: {symbol}\n"
                                f"Размер: {size:.4f}\n"
                                f"Цена входа: {entry_price:.4f}"
                            )

                name, signal, decision = strategy.analyze_symbol(symbol)
                decision = decision or {}

                message = decision.get("message", "Нет комментария")
                indicators = decision.get("indicators", [])
                details = " | ".join(indicators) if indicators else ""

                log_line = f"[{symbol}] {message}"
                if details:
                    log_line += f" | {details}"
                logger.info(log_line)

                if not signal:
                    continue

                log_line = f"[{symbol}] СИГНАЛ: {signal.upper()} — {message}"
                if details:
                    log_line += f" | {details}"
                logger.info(log_line)

                entry = decision.get("entry")
                tp = decision.get("tp")
                sl = decision.get("sl")

                if entry is None or tp is None or sl is None:
                    logger.warning(
                        "[%s] Сигнал без уровней (entry/tp/sl). Пропуск.",
                        symbol,
                    )
                    continue

                success = False
                try:
                    success = orders.enter_position(
                        symbol=symbol,
                        signal=signal,
                        entry=entry,
                        tp=tp,
                        sl=sl,
                    )
                except Exception as exc:
                    logger.warning("[%s] Ошибка открытия позиции: %s", symbol, exc)
                    continue

                if success:
                    new_position = orders.refresh_position(symbol)
                    if new_position and not new_position.get("pending"):
                        tracked_positions[symbol] = {
                            "symbol": symbol,
                            "size": float(new_position.get("size", 0)),
                            "entryPrice": float(new_position.get("entryPrice", 0)),
                        }
                        
                        # Логируем открытие позиции
                        stats_logger.log_trade(
                            symbol=symbol,
                            direction=signal,
                            entry=entry,
                            tp=tp,
                            sl=sl,
                        )

                    if notifier:
                        notifier.send(
                            f"🟢 Открыт ордер\n"
                            f"{log_line}\n"
                            f"Entry: {entry:.6f}\nTP: {tp:.6f}\nSL: {sl:.6f}"
                        )
                else:
                    logger.warning("[%s] Не удалось открыть позицию", symbol)

            time.sleep(max(1, poll_interval))
    except KeyboardInterrupt:
        logger.info("Остановка бота по запросу пользователя.")
    finally:
        if notifier:
            notifier.send("⏹️ Бот остановлен.")


if __name__ == "__main__":
    run_strategy()
