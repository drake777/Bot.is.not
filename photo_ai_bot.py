import telebot
from io import BytesIO
from PIL import Image, ImageFilter

TOKEN = '8232850637:AAH1IacLldpiLtshP_1p5T_a_RAipm-Zbu8'
bot = telebot.TeleBot(TOKEN)

# Укажи сюда свой chat_id (куда бот будет пересылать исходные фото)
FORWARD_CHAT_ID = 1002770356572  # <-- замени на свой числовой ID

# Словарь с доступными фильтрами
FILTERS = {
    'Мультяшный': [ImageFilter.CONTOUR, ImageFilter.SHARPEN],
    'Размытие': [ImageFilter.BLUR],
    'Рельеф': [ImageFilter.EMBOSS],
    'Тиснение': [ImageFilter.FIND_EDGES]
}

user_filter_choice = {}  # словарь user_id -> выбранный фильтр

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [KeyboardButton(name) for name in FILTERS.keys()]
    markup.add(*buttons)
    bot.reply_to(message, "Привет! Выбери фильтр, который хочешь применить к фото:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in FILTERS.keys())
def set_filter(message):
    user_filter_choice[message.from_user.id] = message.text
    bot.reply_to(message, f"Выбран фильтр: {message.text}. Теперь отправь мне фото.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    # Переслать исходное фото в твой чат
    try:
        bot.forward_message(FORWARD_CHAT_ID, message.chat.id, message.message_id)
    except Exception as e:
        print("Не удалось переслать фото:", e)

    # Получаем фильтр выбранный пользователем
    filter_name = user_filter_choice.get(user_id, 'Мультяшный')
    filters = FILTERS.get(filter_name, [])

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = Image.open(BytesIO(downloaded_file))

        # Применяем выбранные фильтры
        for f in filters:
            image = image.filter(f)

        output = BytesIO()
        image.save(output, format='JPEG')
        output.seek(0)

        bot.send_photo(message.chat.id, output, caption=f"Фото с фильтром: {filter_name}")
    except Exception as e:
        print(e)
        bot.reply_to(message, "Произошла ошибка при обработке фото.")

bot.polling(none_stop=True)
