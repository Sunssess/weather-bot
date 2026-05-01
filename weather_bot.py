import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ============================================================
# ОСЫНДА ӨЗ КІЛТТЕРІҢІЗДІ ҚОЙЫҢЫЗ
TELEGRAM_TOKEN = "8077465154:AAEXrF0KIV3Mc9MFZDxeIDcMg-X8Z7D2Ydc"
WEATHER_API_KEY = "40835aff57a1d3f6ff8029fb6eb71f04"
# ============================================================

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------
# Функция 1: /start командасын өңдеу
# Кіріс: /start командасы
# Өңдеу: қарсы алу хабарламасын дайындау
# Шығару: нұсқаулық мәтін
# ---------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user.first_name
    text = (
        f"Сәлем, {user}! 👋\n\n"
        "Мен ауа-райы ботымын. Кез келген қаланың ауа-райын білгіңіз келсе:\n\n"
        "📍 /weather Алматы\n"
        "📍 /weather Астана\n"
        "📍 /weather London\n\n"
        "Сұрақ болса /help командасын жіберіңіз."
    )
    await update.message.reply_text(text)


# ---------------------------------------------------------------
# Функция 2: /weather командасын өңдеу
# Кіріс: /weather <қала атауы>
# Өңдеу: API сұрауы + JSON өңдеу
# Шығару: форматталған ауа-райы хабарламасы
# ---------------------------------------------------------------
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            "❗ Қала атауын жазыңыз.\nМысалы: /weather Алматы"
        )
        return

    city = " ".join(context.args)

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()

        if response.status_code == 200:
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            city_name = data["name"]
            country = data["sys"]["country"]

            text = (
                f"🌍 {city_name}, {country}\n"
                f"{'─' * 25}\n"
                f"🌡 Температура: {temp:.1f}°C\n"
                f"🤔 Сезілетіні: {feels_like:.1f}°C\n"
                f"☁️ Сипаттама: {description.capitalize()}\n"
                f"💧 Ылғалдылық: {humidity}%\n"
                f"💨 Желдің жылдамдығы: {wind_speed} м/с"
            )
            await update.message.reply_text(text)

        elif response.status_code == 404:
            await update.message.reply_text(
                f"❌ «{city}» қаласы табылмады.\n"
                "Қала атауын дұрыс жазып қайталаңыз."
            )
        else:
            await update.message.reply_text(
                "⚠️ Сервер қатесі орын алды. Кейінірек қайталаңыз."
            )

    except requests.exceptions.ConnectionError:
        await update.message.reply_text("🔌 Интернет байланысы жоқ.")
    except requests.exceptions.Timeout:
        await update.message.reply_text("⏱ Сұрау уақыты өтті. Қайталаңыз.")
    except Exception as e:
        logger.error(f"Күтпеген қате: {e}")
        await update.message.reply_text("❗ Күтпеген қате орын алды.")


# ---------------------------------------------------------------
# Функция 3: /help командасын өңдеу
# Кіріс: /help командасы
# Өңдеу: командалар тізімін дайындау
# Шығару: нұсқаулық хабарлама
# ---------------------------------------------------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 Командалар тізімі:\n\n"
        "/start — Ботты іске қосу\n"
        "/weather <қала> — Ауа-райын білу\n"
        "/help — Нұсқаулық\n\n"
        "Мысал:\n"
        "/weather Алматы\n"
        "/weather New York"
    )
    await update.message.reply_text(text)


# ---------------------------------------------------------------
# Негізгі функция — ботты іске қосу
# ---------------------------------------------------------------
def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("Бот іске қосылды...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
