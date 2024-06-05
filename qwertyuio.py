import logging
import telebot
import os

logging.basicConfig(level=logging.INFO)

TOKEN_FILE = 'file.txt'
CHANNEL_ID = '@name'
TOKEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), TOKEN_FILE)

with open(TOKEN_PATH, 'r') as file:
    token = file.read().strip()

bot = telebot.TeleBot(token)
user_name = ''

# Start command
@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    if not is_user_subscribed(chat_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_subscribe = telebot.types.InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/{CHANNEL_ID[1:]}")
        btn_subscribed = telebot.types.InlineKeyboardButton(text="Я подписался✅", callback_data="subscribed")
        markup.add(btn_subscribe, btn_subscribed)
        bot.send_photo(chat_id, photo=open('2222.jpg', 'rb'), caption='Я не буду работать, пока вы не подпишетесь на канал', reply_markup=markup)
        return
    markup = telebot.types.InlineKeyboardMarkup()
    btn_create_request = telebot.types.InlineKeyboardButton(text="Создать заявку", callback_data="create_request")
    markup.add(btn_create_request)
    bot.send_message(chat_id, 'Здравствуйте! Чтобы отправить запрос, используйте команду⏬', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "create_request")
def handle_create_request(call):
    chat_id = call.message.chat.id
    if is_user_subscribed(chat_id):
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_photo(chat_id, photo=open('2222.jpg', 'rb'))
        bot.send_message(chat_id, 'Пожалуйста напишите проблему, с которой вы столкнулись, или же выберите специалистов из предложенных')
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        buttons = ['Дизайнер👨🏻‍🎨', 'Натяжные потолки🪜', 'Мелкие ремонтные работы🛠', 'Репетитор по математике👨‍🏫']
        for button in buttons:
            keyboard.add(button)
        bot.send_message(chat_id, 'Список самых востребованных специалистов📜:', reply_markup=keyboard)
        bot.register_next_step_handler(call.message, process_data)
    else:
        bot.answer_callback_query(call.id, "Вы должны подписаться на канал, прежде чем продолжить")

@bot.callback_query_handler(func=lambda call: call.data == "subscribed")
def handle_subscribed_button(call):
    chat_id = call.message.chat.id
    if is_user_subscribed(chat_id):
        bot.delete_message(chat_id, call.message.message_id)
        markup = telebot.types.InlineKeyboardMarkup()
        btn_create_request = telebot.types.InlineKeyboardButton(text="Создать заявку", callback_data="create_request")
        markup.add(btn_create_request)
        bot.send_message(chat_id, 'Добро пожаловать! Чтобы отправить запрос, используйте команду⏬', reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "Вы должны подписаться на канал, прежде чем продолжить")

# Data state
def process_data(message):
    selected_button = message.text
    bot.send_message(message.chat.id, 'Как вас зовут?')
    bot.register_next_step_handler(message, lambda msg: process_name(msg, selected_button))

# Name state
def process_name(message, selected_button):
    global user_name
    user_name = message.text
    bot.send_message(message.chat.id, 'Какой у вас номер телефона?')
    
    bot.register_next_step_handler(message, lambda msg: process_phone(msg, selected_button))

# Phone state
def process_phone(message, selected_button):
    phone = message.text
    user_id = message.chat.id
    message_text = f"Новая заявка:\nИмя: {user_name} \nНомер: +{phone}\nУслуга: {selected_button}\nID: {user_id}"
    bot.send_message(chat_id='id', text=message_text)
    bot.send_message(message.chat.id, 'Благодарим вас за отправку вашего запроса! Мы свяжемся с вами как можно скорее.(если хотите составить новую заявку, нажмите на /start).')

def is_user_subscribed(chat_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, chat_id)
        return member.status != 'left'
    except telebot.apihelper.ApiException:
        return False

if __name__ == '__main__':
    bot.polling()
