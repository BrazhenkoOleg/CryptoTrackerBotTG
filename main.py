import telebot
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from deep_translator import GoogleTranslator
from utils.db_manager import init_db, insert_crypto_price, get_recent_prices
from utils.crypto_tracker import get_crypto_price
from config import BOT_TOKEN, SUPPORTED_CRYPTOCURRENCIES, SUPPORTED_CURRENCIES

bot = telebot.TeleBot(BOT_TOKEN)
user_settings = {}  # Сохраняет настройки пользователя (криптовалюта, валюта)

# Функция для перевода текста
def translate_text(text, lang_code):
    try:
        return GoogleTranslator(source='auto', target=lang_code).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# Инициализация базы данных при запуске бота
init_db()

# Создаем меню с настройками
def create_settings_menu(lang_code='en'):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton(translate_text("💰 Выбрать криптовалюту", lang_code)),
        KeyboardButton(translate_text("💵 Выбрать валюту", lang_code))
    )
    markup.add(
        KeyboardButton(translate_text("📜 Просмотр истории запросов", lang_code)),
        KeyboardButton(translate_text("📈 Получить цену", lang_code))
    )
    return markup

# Настраиваем язык по умолчанию на основе языка пользователя
@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    user_language_code = message.from_user.language_code
    lang_code = user_language_code if user_language_code else 'en'
    user_settings[user_id] = {'language': lang_code, 'crypto': 'BTC', 'currency': 'USD'}
    bot.send_message(
        message.chat.id,
        translate_text("Добро пожаловать! Используйте меню для настройки.", lang_code),
        reply_markup=create_settings_menu(lang_code)
    )

# Обработка нажатия на кнопки
@bot.message_handler(func=lambda message: True)
def handle_settings(message):
    user_id = message.from_user.id
    lang_code = user_settings[user_id]['language']
    
    if message.text == translate_text("💰 Выбрать криптовалюту", lang_code):
        bot.send_message(message.chat.id, translate_text("Выберите криптовалюту:", lang_code), reply_markup=create_crypto_keyboard(lang_code))
    elif message.text == translate_text("💵 Выбрать валюту", lang_code):
        bot.send_message(message.chat.id, translate_text("Выберите валюту:", lang_code), reply_markup=create_currency_keyboard(lang_code))
    elif message.text == translate_text("📈 Получить цену", lang_code):
        get_price(message)
    elif message.text == translate_text("📜 Просмотр истории запросов", lang_code):
        show_history(message)

# Создаем клавиатуру для выбора криптовалюты
def create_crypto_keyboard(lang_code):
    markup = InlineKeyboardMarkup()
    for crypto in SUPPORTED_CRYPTOCURRENCIES:
        button = InlineKeyboardButton(crypto, callback_data=f"crypto_{crypto}")
        markup.add(button)
    return markup

# Выбор криптовалюты
@bot.callback_query_handler(func=lambda call: call.data.startswith("crypto_"))
def choose_crypto(call):
    crypto = call.data.split('_')[1]
    user_id = call.from_user.id
    user_settings[user_id]['crypto'] = crypto
    lang_code = user_settings[user_id]['language']
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, translate_text("Криптовалюта выбрана!", lang_code), reply_markup=create_settings_menu(lang_code))

# Создаем клавиатуру для выбора валюты
def create_currency_keyboard(lang_code):
    markup = InlineKeyboardMarkup()
    for currency_code in SUPPORTED_CURRENCIES:
        button = InlineKeyboardButton(currency_code, callback_data=f"currency_{currency_code}")
        markup.add(button)
    return markup

# Выбор валюты
@bot.callback_query_handler(func=lambda call: call.data.startswith("currency_"))
def choose_currency(call):
    currency_code = call.data.split('_')[1]
    user_id = call.from_user.id
    user_settings[user_id]['currency'] = currency_code
    lang_code = user_settings[user_id]['language']
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, translate_text("Валюта выбрана!", lang_code), reply_markup=create_settings_menu(lang_code))

# Получение цены через команду /price
@bot.message_handler(commands=['price'])
@bot.message_handler(func=lambda message: message.text == "📈 Получить цену")
def get_price(message):
    user_id = message.from_user.id
    settings = user_settings.get(user_id, {'language': 'en', 'crypto': 'BTC', 'currency': 'USD'})
    lang_code = settings['language']
    crypto = settings['crypto']
    currency = settings['currency']
    
    price = get_crypto_price(crypto, currency)
    if price is not None:
        message_text = f"Текущая цена {crypto}: {price} {currency}"
        bot.send_message(message.chat.id, translate_text(message_text, lang_code))
        insert_crypto_price(user_id, crypto, currency, price)
    else:
        error_message = "Ошибка при получении данных."
        bot.send_message(message.chat.id, translate_text(error_message, lang_code))

# Функция для показа последних 10 запросов
def show_history(message):
    user_id = message.from_user.id
    lang_code = user_settings[user_id]['language']
    history = get_recent_prices(user_id)

    if history:
        history_text = translate_text("Последние запросы:", lang_code) + "\n"
        for crypto, currency, price, timestamp in history:
            # Форматируем дату и время
            timestamp_str = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y %H:%M:%S")
            history_text += f"{crypto} -> {price:.2f} {currency}\n" + translate_text("Дата и время:", lang_code) + f" {timestamp_str}\n\n"
        
        bot.send_message(message.chat.id, history_text)
    else:
        bot.send_message(message.chat.id, translate_text("История запросов пуста.", lang_code))

if __name__ == "__main__":
    bot.polling(none_stop=True)
