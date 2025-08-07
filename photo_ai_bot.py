import telebot
from io import BytesIO
from PIL import Image, ImageFilter, ImageOps

TOKEN = '8232850637:AAH1IacLldpiLtshP_1p5T_a_RAipm-Zbu8'
CHANNEL_CHAT_ID = -1001234567890  # <-- Вставь сюда chat_id своего канала

bot = telebot.TeleBot(TOKEN)

FILTERS = {
    'BLUR': [ImageFilter.BLUR],
    'CONTOUR': [ImageFilter.CONTOUR],
    'DETAIL': [ImageFilter.DETAIL],
    'EDGE_ENHANCE': [ImageFilter.EDGE_ENHANCE],
    'EMBOSS': [ImageFilter.EMBOSS],
    'SHARPEN': [ImageFilter.SHARPEN],
    'SMOOTH': [ImageFilter.SMOOTH],
    'FIND_EDGES': [ImageFilter.FIND_EDGES],
    'BLACK_WHITE': ['BLACK_WHITE']  # Особый фильтр, обрабатываем отдельно
}

user_filter_choices = {}

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def make_filter_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    buttons = [KeyboardButton(name) for name in FILTERS.keys()]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Выбери фильтр для обработки фото.", reply_markup=make_filter_keyboard())

@bot.message_handler(commands=['done'])
def finish_selection(message):
    user_id = message.from_user.id
    selected = user_filter_choices.get(user_id, [])
    if not selected:
        bot.reply_to(message, "Ты не выбрал ни одного фильтра. Использую фильтр по умолчанию: CONTOUR + SHARPEN.")
        user_filter_choices[user_id] = ['CONTOUR', 'SHARPEN']
    else:
        bot.reply_to(message, f"Выбраны фильтры: {', '.join(selected)}. Теперь пришли фото.")

@bot.message_handler(commands=['clear'])
def clear_filters(message):
    user_id = message.from_user.id
    user_filter_choices.pop(user_id, None)
    bot.reply_to(message, "Фильтры сброшены. Фото будет отправляться без обработки.")

@bot.message_handler(func=lambda message: message.text in FILTERS.keys())
def add_filter(message):
    user_id = message.from_user.id
    selected = user_filter_choices.get(user_id, [])
    if message.text not in selected:
        selected.append(message.text)
        user_filter_choices[user_id] = selected
        bot.reply_to(message, f"Фильтр '{message.text}' добавлен. Выбрано: {', '.join(selected)}")
    else:
        bot.reply_to(message, f"Фильтр '{message.text}' уже выбран.")
    bot.send_message(message.chat.id, "Выбирай еще фильтры или напиши /done, чтобы продолжить.", reply_markup=make_filter_keyboard())

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    filters = user_filter_choices.get(user_id)

    # Переслать исходное фото в канал
    try:
        bot.forward_message(CHANNEL_CHAT_ID, message.chat.id, message.message_id)
    except Exception as e:
        print("Ошибка пересылки в канал:", e)

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = Image.open(BytesIO(downloaded_file))

        if not filters or len(filters) == 0:
            # Нет фильтров — отправляем оригинал
            bot.send_photo(message.chat.id, message.photo[-1].file_id, caption="Фото без обработки")
            return

        # Применяем фильтры
        for f_name in filters:
            if f_name == 'BLACK_WHITE':
                image = ImageOps.grayscale(image)
            else:
                for f in FILTERS[f_name]:
                    image = image.filter(f)

        output = BytesIO()
        output.name = 'processed.jpg'
        image.save(output, format='JPEG')
        output.seek(0)

        bot.send_photo(message.chat.id, output, caption=f"Фото с фильтрами: {', '.join(filters)}")

    except Exception as e:
        bot.reply_to(message, f"Ошибка обработки фото: {e}")

bot.polling(none_stop=True)
