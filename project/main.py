import sys
import logging
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "databases_methods"))

import telebot
from telebot import types
from students_handler import setup_student_handlers, students_keyboard
from admins_handler import admin_keyboard, setup_admin_handlers
from main_admins_handler import main_admin_keyboard, setup_main_admin_handlers

from databases_methods.main_admin_methods import get_main_admin
from databases_methods.users_methods import add_user, get_user
from databases_methods.students_methods import add_student
from databases_methods.key_for_admin import search_key
from databases_methods.students_methods import update_student_info, get_student_by_tg_id
from databases_methods.admins_methods import add_admin, get_admin
from dotenv import load_dotenv

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
        # get_main_admin(tg_id)

        if get_main_admin(tg_id):
            bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Выберите действие:',
                             reply_markup = main_admin_keyboard())
        elif get_admin(tg_id) != None:
            bot.send_message(message.chat.id,
                             f'Здравствуйте {message.from_user.first_name}! Вы уже зарегистрированы, как администратор. Выберите действие:',
                             reply_markup = admin_keyboard())
        elif get_student_by_tg_id(tg_id) != None:
            bot.send_message(message.chat.id,
                             f'Здравствуйте {message.from_user.first_name}! Вы уже зарегистрированы, как студент. Выберите действие:',
                             reply_markup = students_keyboard())
        else:
            bot.send_message(message.chat.id,
                             f'Здравствуйте, {message.from_user.first_name}! Вы еще не зарегистрированы. Введите своё ФИО также, как написано в ведомости.')
            bot.register_next_step_handler(message, process_fio)
    except Exception as e:
        logging.error(f"Ошибка в команде /start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз позже.")



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
        markup.add(types.InlineKeyboardButton('Я преподователь или ассистент', callback_data = 'new_admin'))

        bot.send_message(message.chat.id, f"Спасибо, {first_name}! Ваши данные сохранены. Выберите, кем вы являетесь:",
                         reply_markup = markup)
    except Exception as e:
        logging.error(f"Ошибка в process_fio: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке имени. Попробуйте еще раз.")


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
        bot.send_message(callback.message.chat.id, "Произошла ошибка. Попробуйте еще раз.")


# узнаем номер группы студента
def process_group(message):
    try:
        group = message.text
        if add_student(message.from_user.id, group):
            bot.send_message(message.chat.id, "Ваши данные сохранены! Выберите следующее действие:",
                             reply_markup = students_keyboard())
        else:
            bot.send_message(message.chat.id,
                             "Ваши данные сохранены, но вы не найдены в списке лектора.\n"
                             "Проверьте, совпадают ли ваши группа и имя с ведомостью. Вы в любой момент можете изменить данные.\n"
                             "Выберите следующее действие:",
                             reply_markup = students_keyboard())
    except Exception as e:
        logging.error(f"Ошибка в process_group: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке группы. Попробуйте еще раз.")


# регаемся как ассистент
def process_new_admin(message):
    try:
        key = message.text
        res = search_key(key)
        if res:
            bot.send_message(message.chat.id,
                             "Введите группы, за которые вы ответственны через запятую. Например: 241, 243, 244")
            bot.register_next_step_handler(message, process_group_for_admin)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Я студент', callback_data = 'student'))
            markup.add(types.InlineKeyboardButton('Я преподователь или ассистент', callback_data = 'new_admin'))
            bot.send_message(message.chat.id,
                             "Не удалось зарегистрироваться. Возможно, вы ввели неверный код, или код уже устарел. \n"
                             "Выберите следующее действие:",
                             reply_markup = markup)
    except Exception as e:
        logging.error(f"Ошибка в process_new_admin: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")


def process_group_for_admin(message):
    try:
        groups = message.text
        list_of_groups = groups.split()
        groups = ''
        for group in list_of_groups:
            groups += group + ' '
        groups = groups[:-1]
        add_admin(message.from_user.id, message.from_user.username, groups)
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались, теперь вам доступны права администратора!",
                         reply_markup = admin_keyboard())
    except Exception as e:
        logging.error(f"Ошибка в process_group_for_admin: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке групп. Попробуйте еще раз.")


bot.polling(none_stop = True)
