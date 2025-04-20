import logging
from telebot import types
import re
import os
from databases_methods.admins_methods import update_admin_info as update_admin_info_db, get_admin
from databases_methods.tasks_methods import get_task_for_admin, get_task_by_pk
from databases_methods.key_for_admin import search_key
from databases_methods.main_admin_methods import add_main_admin
from main_admins_handler import main_admin_keyboard

logging.basicConfig(
    filename = "bot_errors.log",
    level = logging.ERROR,
    format = "%(asctime)s - %(levelname)s - %(message)s",
)


def admin_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Стать главным администратором', callback_data = 'become_main_admin'))
    markup.add(types.InlineKeyboardButton('Изменить информацию о себе', callback_data = 'admin_edit_info'))
    markup.add(
        types.InlineKeyboardButton('Просмотр доступных работ', callback_data = 'admin_task'))
    return markup


def setup_admin_handlers(bot):
    @bot.callback_query_handler(func = lambda callback: callback.data in ['become_main_admin'])
    def became_main_admin_from_admin(callback):
        try:
            bot.send_message(callback.message.chat.id, f"Введите код доступа:")
            bot.register_next_step_handler(callback.message, process_main_admin_from_admin)
        except Exception as e:
            logging.error(f"Ошибка в became_main_admin_from_admin: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка. Попробуйте позже.\n/start")

    def process_main_admin_from_admin(message):
        try:
            key = message.text
            if key == '/start':
                bot.send_message(message.chat.id,
                                 "Выберите следующее действие:",
                                 reply_markup = admin_keyboard())
                return
            res = search_key(key)
            if res and res[-1] == 'main':
                add_main_admin(message.from_user.id, message.from_user.username, '', message.from_user.first_name)
                bot.send_message(message.chat.id,
                                 "Вы зарегистрированы как главный администратор!",
                                 reply_markup = main_admin_keyboard())
            else:
                bot.send_message(message.chat.id,
                                 "Не удалось зарегистрироваться. "
                                 "Возможно, вы ввели неверный код, или код уже устарел. \n"
                                 "Попробуйте ввести код ещё раз или нажмите /start:")
                bot.register_next_step_handler(message, process_main_admin_from_admin)
                return
        except Exception as e:
            logging.error(f"Ошибка в process_main_admin_from_admin: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.\n/start")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['admin_edit_info'])
    def update_admin_info(callback):
        try:
            admin = get_admin(callback.message.chat.id)
            if admin:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Изменить имя', callback_data = 'update_admin_name'))
                markup.add(types.InlineKeyboardButton('Изменить свой список групп',
                                                      callback_data = 'update_admin_group'))
                bot.send_message(callback.message.chat.id, f"Ваше имя: {admin[2]}.\n"
                                                           f"Ваши группы: {admin[3]}.\n"
                                                           f"Выберите, что вы хотите изменить:",
                                 reply_markup = markup)
            else:
                bot.send_message(callback.message.chat.id, f"Вас больше нет в списке администраторов. Нажмите /start.")

        except Exception as e:
            logging.error(f"Ошибка в update_admin_info: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка. Попробуйте позже.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['update_admin_name', 'update_admin_group'])
    def handle_update_request(callback):
        try:
            if callback.data == 'update_admin_name':
                bot.send_message(callback.message.chat.id, f"Введите новое имя")
                bot.register_next_step_handler(callback.message, process_update_name)
            else:
                bot.send_message(callback.message.chat.id, f"Введите новый список групп через запятую. "
                                                           f"Например: 234, 235, 236")
                bot.register_next_step_handler(callback.message, process_update_group)
        except Exception as e:
            logging.error(f"Ошибка в handle_update_request: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка. Попробуйте позже.")

    def process_update_name(message):
        try:
            new_name = message.text
            if update_admin_info_db(message.from_user.id, new_full_name = new_name):
                admin = get_admin(message.from_user.id)
                bot.send_message(message.chat.id, "Информация изменена!\n"
                                                  f"Ваше имя: {admin[2]}\n"
                                                  f"Ваша группа: {admin[3]}",
                                 reply_markup = admin_keyboard())
            else:
                bot.send_message(message.chat.id, "Не удалось изменить информацию")
        except Exception as e:
            logging.error(f"Ошибка в process_update_name: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")

    def process_update_group(message):
        try:
            new_group = message.text.strip()
            if new_group == '/start':
                bot.send_message(message.chat.id,
                                 "Выберите следующее действие:",
                                 reply_markup = admin_keyboard())
                return
            if re.fullmatch(r"(\d+)(,\s*\d+)*", new_group):
                bot.send_message(message.chat.id, f'Неправильный формат! Попробуйте снова:')
                bot.register_next_step_handler(message, process_update_group)
                return
            if update_admin_info_db(message.from_user.id, new_groups_of_students = new_group):
                admin = get_admin(message.from_user.id)
                bot.send_message(message.chat.id, "Информация изменена!\n"
                                                  f"Ваше имя: {admin[2]}\n"
                                                  f"Ваша группа: {admin[3]}",
                                 reply_markup = admin_keyboard())
            else:
                bot.send_message(message.chat.id, "Не удалось изменить информацию")
        except Exception as e:
            logging.error(f"Ошибка в process_update_group: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['admin_task'])
    def get_list_of_task_for_admin(callback):
        try:
            admin = get_admin(callback.message.chat.id)
            if admin:
                task = get_task_for_admin(admin[3])
                if task:
                    text_message = 'Доступные задания:\n' + task + 'Выберите действие ниже или нажмите /start'
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton('Получить файл с ответами', callback_data = 'get_ans_pdf_for_admin'))
                    bot.send_message(callback.message.chat.id, text_message, reply_markup = markup)
                else:
                    bot.send_message(callback.message.chat.id, "Нет доступных заданий",
                                     reply_markup = admin_keyboard())
            else:
                bot.send_message(callback.message.chat.id,
                                 "Вы не найдены в базе данных. Возможно, вас удалили из администраторов. "
                                 "Для продолжения нажмите /start")
        except Exception as e:
            logging.error(f"Ошибка в get_list_of_task_for_admin: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка. Попробуйте позже.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['get_ans_pdf_for_admin'])
    def get_ans_for_admin(callback):
        try:
            bot.send_message(callback.message.chat.id, "Введите номер задания:")
            bot.register_next_step_handler(callback.message, process_get_task_id_from_admin)
        except Exception as e:
            logging.error(f"Ошибка в get_ans_for_admin: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка. Попробуйте позже.")

    def process_get_task_id_from_admin(message):
        try:
            task_id = message.text.strip()
            if task_id == '/start':
                bot.send_message(message.chat.id,
                                 "Выберите следующее действие:",
                                 reply_markup = admin_keyboard())
                return
            task_info = get_task_by_pk(task_id)
            admin_info = get_admin(message.from_user.id)
            if task_info and task_info[5] == 0 or not task_info or not task_id.isdigit():
                bot.send_message(message.chat.id, "Вы ввели неправильный номер, попробуйте ещё раз или введите /start:")
                bot.register_next_step_handler(message, process_get_task_id_from_admin)
                return
            groups_string = admin_info[3]
            groups = [group.strip() for group in groups_string.split(',')]

            for group in groups:
                pdf_path_task = f"task/{task_info[1]}/{task_info[1]}_condition_for_group_{group}.pdf"
                pdf_path_ans = f"task/{task_info[1]}/{task_info[1]}_ans_for_group_{group}.pdf"
                pdf_path_solution = f"task/{task_info[1]}/{task_info[1]}_solution_for_group_{group}.pdf"

                if os.path.exists(pdf_path_task) and os.path.exists(pdf_path_ans) and os.path.exists(pdf_path_solution):
                    with (open(pdf_path_task, "rb") as pdf1, open(pdf_path_ans, "rb") as pdf2,
                          open(pdf_path_solution, "rb") as pdf3):
                        bot.send_document(message.chat.id, pdf1,
                                          caption = f'Задание: {task_info[1]}\nУсловия для группы: {group}')
                        bot.send_document(message.chat.id, pdf2,
                                          caption = f'Задание: {task_info[1]}\nОтветы для группы: {group}')
                        bot.send_document(message.chat.id, pdf3,
                                          caption = f'Задание: {task_info[1]}\nРешения для группы: {group}')
            bot.send_message(
                message.chat.id,
                f'Выберите следующее действие', reply_markup = admin_keyboard())

        except Exception as e:
            logging.error(f"Ошибка в def process_get_task_id_from_student: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")
