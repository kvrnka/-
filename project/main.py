import sys
import logging
import os
import re
import time
import telebot
from telebot import types
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "databases_methods"))

from students_handler import setup_student_handlers, students_keyboard
from admins_handler import admin_keyboard, setup_admin_handlers
from main_admins_handler import main_admin_keyboard, setup_main_admin_handlers
from databases_methods.main_admin_methods import get_main_admin, add_main_admin
from databases_methods.users_methods import add_user
from databases_methods.students_methods import add_student
from databases_methods.key_for_admin import search_key
from databases_methods.students_methods import get_student_by_tg_id
from databases_methods.admins_methods import add_admin, get_admin

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(
    filename= "bot_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

setup_student_handlers(bot)
setup_admin_handlers(bot)
setup_main_admin_handlers(bot)


@bot.message_handler(commands = ['start'])
def start(message):
    try:
        tg_id = message.from_user.id
        if get_main_admin(tg_id):
            bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Выберите действие:',
                             reply_markup = main_admin_keyboard())
        elif get_admin(tg_id):
            bot.send_message(message.chat.id,
                             f'Здравствуйте {message.from_user.first_name}! '
                             f'Вы уже зарегистрированы, как администратор. Выберите действие:',
                             reply_markup = admin_keyboard())
        elif get_student_by_tg_id(tg_id):
            bot.send_message(message.chat.id,
                             f'Здравствуйте {message.from_user.first_name}! '
                             f'Вы уже зарегистрированы, как студент. Выберите действие:',
                             reply_markup = students_keyboard())
        else:
            bot.send_message(message.chat.id,
                             f'Здравствуйте, {message.from_user.first_name}! '
                             f'Вы еще не зарегистрированы. Введите своё ФИО также, как написано в ведомости.')
            bot.register_next_step_handler(message, process_fio)
    except Exception as e:
        logging.error(f"Ошибка в команде /start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз позже.\n/start")


# узнаем фио пользователя
def process_fio(message):
    try:
        full_name = message.text.strip()

        parts = full_name.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Ошибка! Вы ввели неполное имя.")
            bot.register_next_step_handler(message, process_fio)  # Просим ввести снова
            return

        first_name = parts[1]
        name = ''
        for n in parts:
            n = n.strip()
            name += n + ' '

        name = name[:-1]
        tg_id = message.from_user.id
        tg_username = message.from_user.username

        add_user(tg_id, tg_username, name)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Я студент', callback_data = 'student'))
        markup.add(types.InlineKeyboardButton('Я преподаватель или ассистент', callback_data = 'new_admin'))

        bot.send_message(message.chat.id, f"Спасибо, {first_name}! Ваши данные сохранены. Выберите, кем вы являетесь:",
                         reply_markup = markup)
    except Exception as e:
        logging.error(f"Ошибка в process_fio: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке имени. Попробуйте позже.\n/start")


# продолжение регистрации
@bot.callback_query_handler(func = lambda callback: callback.data in ["new_admin", "student"])
def continue_registration(callback):
    try:
        if callback.data == 'new_admin':
            bot.send_message(callback.message.chat.id, "Введите код доступа")
            bot.register_next_step_handler(callback.message, process_new_admin)
        else:
            bot.send_message(callback.message.chat.id, "Введите номер вашей группы")
            bot.register_next_step_handler(callback.message, process_group)
    except Exception as e:
        logging.error(f"Ошибка в continue_registration: {e}")
        bot.send_message(callback.message.chat.id, "Произошла ошибка. Попробуйте позже.\n/start")


# узнаем номер группы студента
def process_group(message):
    try:
        group = message.text.strip()
        if not group.isdigit():
            bot.send_message(message.chat.id, f'Группа должна состоять только из цифр. Введите ещё раз:')
            bot.register_next_step_handler(message, process_group)
            return
        if add_student(message.from_user.id, int(group)):
            bot.send_message(message.chat.id, "Ваши данные сохранены, вы найдены в списке лектора! "
                                              "Выберите следующее действие:",
                             reply_markup = students_keyboard())
        else:
            bot.send_message(message.chat.id,
                             "Ваши данные сохранены, но вы не найдены в списке лектора.\n"
                             "Проверьте, совпадают ли ваши группа и имя с ведомостью.\n"
                             "Вы в любой момент можете изменить данные.\n"
                             "Выберите следующее действие:",
                             reply_markup = students_keyboard())
    except Exception as e:
        logging.error(f"Ошибка в process_group: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке группы. Попробуйте позже.\n/start")


def process_new_admin(message):
    try:
        key = message.text
        if key == '/start':
            return
        res = search_key(key)
        if not res:
            bot.send_message(message.chat.id,
                             "Не удалось зарегистрироваться. "
                             "Возможно, вы ввели неверный код, или код уже устарел. \n"
                             "Попробуйте ввести код ещё раз или нажмите /start:")
            bot.register_next_step_handler(message, process_new_admin)
            return
        elif res[-1] == 'main':
            add_main_admin(message.from_user.id, message.from_user.username, '', message.from_user.first_name)
            bot.send_message(message.chat.id,
                             "Вы зарегистрированы, как главный администратор!")
        elif res[-1] == 'not_main':
            bot.send_message(message.chat.id,
                             "Введите группы, за которые вы ответственны через запятую и пробел. "
                             "Например: 241, 243, 244")
            bot.register_next_step_handler(message, process_group_for_admin)
    except Exception as e:
        logging.error(f"Ошибка в process_new_admin: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.\n/start")


def process_group_for_admin(message):
    try:
        groups = message.text.strip()
        if groups == '/start':
            return
        if not re.fullmatch(r"^\d+(,\s*\d+)*$", groups):
            bot.send_message(message.chat.id, f'Неправильный формат! Попробуйте снова или нажмите /start:')
            bot.register_next_step_handler(message, process_group_for_admin)
            return
        add_admin(message.from_user.id, message.from_user.username, groups)
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались, теперь вам доступны права администратора!",
                         reply_markup = admin_keyboard())
    except Exception as e:
        logging.error(f"Ошибка в process_group_for_admin: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке групп. Попробуйте позже.\n/start")


while True:
    try:
        print("Бот запущен...")
        bot.polling(none_stop=True, timeout=10, long_polling_timeout=10)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)  # Подождать 5 секунд и перезапустить
