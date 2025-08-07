import telebot
from io import BytesIO
from PIL import Image, ImageFilter

TOKEN = '8232850637:AAF38n4pLP6QA7FJi0A34K_etBpMF4k4Kzw'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Пришли мне фото, я применю мультяшный стиль.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = Image.open(BytesIO(downloaded_file))

        # Применяем мультяшный фильтр (контуры + резкость)
        image = image.filter(ImageFilter.CONTOUR)
        image = image.filter(ImageFilter.SHARPEN)

        output = BytesIO()
        image.save(output, format='JPEG')
        output.seek(0)

        bot.send_photo(message.chat.id, output, caption="Вот твое мультяшное фото!")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обработке фото.")

bot.polling(none_stop=True)
