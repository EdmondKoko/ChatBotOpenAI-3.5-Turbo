import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler

load_dotenv()

# получаем токен с помощью переменной окружения из .env
token = os.getenv('TELEGRAM_TOKEN')
OpenAIKey = os.getenv('OpenAIKey')

# создаем экземпляр класса OpenAI
client = OpenAI(
    api_key=OpenAIKey
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# функция запуска бота
def start_bot(update, context):
    # Получаем информацию о чате, из которого пришло сообщение,
    # и сохраняем в переменную chat
    chat = update.effective_chat
    # Получаем имя пользователя
    name = update.message.from_user.first_name
    # Создаем кнопку
    button = ReplyKeyboardMarkup([
        ['/start', 'Давай пообщаемся?']], resize_keyboard=True)
    try:
        # В ответ на комманду '/start'
        # будет отправлено 'Привет username! Я готов ебашить как негр!'
        context.bot.send_message(chat_id=chat.id,
                                 text='Привет {}! Я готов ебашить как негр!'
                                 .format(name), reply_markup=button)
    # Перехватываем исключения
    except Exception as error:
        # Выводим их в консоль
        logging.error(error, exc_info=True)
        # Отправляем сообщение пользователю
        context.bot.send_message(chat_id=chat.id,
                                 text='Что-то пошло не так, попробуйте еще раз')


# функция обработки текстовых сообщений и отправки ответа сгенерированным OpenAI
def text_handler_bot(update, context):
    # Получаем информацию о чате, из которого пришло сообщение,
    # и сохраняем в переменную chat
    chat = update.effective_chat
    # Получаем текст сообщения
    question = update.message.text
    # Вылавливаем исключения
    try:
        # Отправляем сообщение клиенту OpenAI
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=question,
            temperature=0.9,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
        # Сохраняем ответ в переменную
        answer = response.choices[0].text
        # В ответ на любое текстовое сообщение будет отправлено ответ бота
        context.bot.send_message(chat_id=chat.id,
                                 text=answer)
    # Исключения перехватываются и выводятся в консоль и отправляются в чат бота
    except(ValueError, TypeError, ConnectionError) as error:
        # Выводим их в консоль
        logging.error(error, exc_info=True)
        # Отправляем сообщение пользователю
        context.bot.send_message(chat_id=chat.id,
                                 text='Что-то пошло не так, попробуйте еще раз')


# Исполняемый код, не запускается при импорте
if __name__ == '__main__':
    # Экземпляр класса Updater, который будет обрабатывать входящие сообщения
    updater = Updater(token=token)
    # Регистрируется обработчик CommandHandler;
    # из команды '/start' он будет вызывать функцию start_bot
    updater.dispatcher.add_handler(CommandHandler('start', start_bot))
    # Регистрируется обработчик MessageHandler;
    # из всех полученных сообщений он будет выбирать только текстовые сообщения
    # и передавать их в функцию text_handler_bot
    updater.dispatcher.add_handler(MessageHandler(Filters.all, text_handler_bot))
    # Метод start_polling() запускает процесс polling,
    # приложение начнёт отправлять регулярные запросы для получения обновлений.
    # Интервал отправки обновлений - 10 сек
    updater.start_polling(poll_interval=10)
    # Бот будет работать до тех пор, пока не нажмете Ctrl-C
    updater.idle()
