import logging
import os
from telebot import types
import re
from databases_methods.students_methods import update_student_info, get_student_by_tg_id
from databases_methods.tasks_methods import get_publish_task_for_student_by_group, get_task_by_pk
from databases_methods.key_for_admin import search_key
from databases_methods.admins_methods import add_admin
from databases_methods.main_admin_methods import add_main_admin
from admins_handler import admin_keyboard

logging.basicConfig(
    filename = "bot_errors.log",
    level = logging.ERROR,
    format = "%(asctime)s - %(levelname)s - %(message)s",
)


def students_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Изменить информацию о себе', callback_data = 'edit_info'))
    markup.add(
        types.InlineKeyboardButton('Просмотр доступных работ', callback_data = 'get_task_for_student'))
    return markup


def setup_student_handlers(bot):
    @bot.callback_query_handler(func = lambda callback: callback.data in ['edit_info'])
    def continue_registration(callback):
        try:
            student = get_student_by_tg_id(callback.message.chat.id)
            if student:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Зарегистрироваться как преподаватель или ассистент',
                                                      callback_data = 'new_admin_from_student'))
                markup.add(types.InlineKeyboardButton('Изменить имя', callback_data = 'update_name'))
                markup.add(types.InlineKeyboardButton('Изменить группу', callback_data = 'update_group'))
                bot.send_message(callback.message.chat.id, f"Ваше имя: {student[2]}.\n"
                                                           f"Ваша группа: {student[1]}.\n"
                                                           f"Выберите, что вы хотите изменить:",
                                 reply_markup = markup)
            else:
                bot.send_message(callback.message.chat.id, f'Вы не найдены в базе данных, попробуйте снова',
                                 reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в continue_registration: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте позже.\n/start")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['new_admin_from_student',
                                                                          'update_name', 'update_group'])
    def handle_update_request(callback):
        try:
            if callback.data == 'new_admin_from_student':
                bot.send_message(callback.message.chat.id, "Введите код доступа")
                bot.register_next_step_handler(callback.message, process_new_admin_from_student)
            elif callback.data == 'update_name':
                bot.send_message(callback.message.chat.id, f"Введите новое имя")
                bot.register_next_step_handler(callback.message, process_update_name)
            if callback.data == 'update_group':
                bot.send_message(callback.message.chat.id, f"Введите новую группу")
                bot.register_next_step_handler(callback.message, process_update_group)
        except Exception as e:
            logging.error(f"Ошибка в handle_update_request: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    def process_new_admin_from_student(message):
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
                bot.register_next_step_handler(message, process_new_admin_from_student)
                return
            elif res[-1] == 'not_main':
                bot.send_message(message.chat.id,
                                 "Введите группы, за которые вы ответственны через запятую. Например: 241, 243, 244")
                bot.register_next_step_handler(message, process_group_for_admin_from_student)
            elif res[-1] == 'main':
                add_main_admin(message.from_user.id, message.from_user.username, '', message.from_user.first_name)
                bot.send_message(message.chat.id,
                                 "Вы зарегистрированы, как главный администратор!")
        except Exception as e:
            logging.error(f"Ошибка в process_new_admin: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.\n/start")

    def process_group_for_admin_from_student(message):
        try:
            groups = message.text.strip()
            if re.fullmatch(r"(\d+)(,\s*\d+)*", groups):
                bot.send_message(message.chat.id, f'Неправильный формат! Попробуйте снова:')
                bot.register_next_step_handler(message, process_group_for_admin_from_student)
                return
            add_admin(message.from_user.id, message.from_user.username, groups)
            bot.send_message(message.chat.id,
                             "Вы успешно зарегистрировались, теперь вам доступны права администратора!",
                             reply_markup = admin_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_group_for_admin_from_student: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка при обработке групп. Попробуйте позже.\n/start")

    def student_is_found(check, student):
        try:
            if not check[0]:
                bot.send_message(student[0], "Не удалось обновить информацию", reply_markup = students_keyboard())
            elif check[0] and check[1]:
                bot.send_message(student[0], "Информация изменена, вы найдены в списке лектора!\n"
                                             f"Ваше имя: {student[2]}\n"
                                             f"Ваша группа: {student[1]}",
                                 reply_markup = students_keyboard())
            elif check[0] and not check[1]:
                bot.send_message(student[0], "Информация изменена, но вы не найдены в списке лектора.\n"
                                             f"Ваше имя: {student[2]}\n"
                                             f"Ваша группа: {student[1]}",
                                 reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_update_name: {e}")
            bot.send_message(student[0], "Произошла ошибка! Попробуйте позже.\n/start")

    def process_update_name(message):
        try:
            new_name = message.text
            check = update_student_info(message.from_user.id, None, new_name)
            student = get_student_by_tg_id(message.from_user.id)
            if student:
                student_is_found(check, student)
            else:
                bot.send_message(message.chat.id, f'Вы не найдены в базе данных', reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_update_name: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    def process_update_group(message):
        try:
            new_group = message.text
            if not new_group.isdigit():
                bot.send_message(message.chat.id, f'Группа должна состоять только из цифр. Введите ещё раз:')
                bot.register_next_step_handler(message, process_update_group)
                return
            check = update_student_info(message.from_user.id, int(new_group), None)
            student = get_student_by_tg_id(message.from_user.id)
            if student:
                student_is_found(check, student)
            else:
                bot.send_message(message.chat.id, f'Вы не найдены в базе данных', reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_update_group: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте позже.\n/start")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['get_task_for_student'])
    def get_list_of_task_for_student(callback):
        try:
            student = get_student_by_tg_id(callback.message.chat.id)
            if student:
                group = student[1]
                task = get_publish_task_for_student_by_group(group)
                if task:
                    text_message = 'Доступные задания:\n' + task + 'Выберите действие ниже или нажмите /start'
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton('Получить файл с заданием', callback_data = 'get_pdf_for_student'))
                    bot.send_message(callback.message.chat.id, text_message, reply_markup = markup)
                else:
                    bot.send_message(callback.message.chat.id, "Нет доступных заданий",
                                     reply_markup = students_keyboard())
            else:
                bot.send_message(callback.message.chat.id, f'Вы не найдены в базе данных, попробуйте ещё раз.',
                                 reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в def get_list_of_task_for_student: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['get_pdf_for_student'])
    def get_task_for_student(callback):
        try:
            bot.send_message(callback.message.chat.id, "Введите номер задания:")
            bot.register_next_step_handler(callback.message, process_get_task_id_from_student)
        except Exception as e:
            logging.error(f"Ошибка в def get_list_of_task_for_student: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз позже.\n/start")

    def process_get_task_id_from_student(message):
        try:
            task_id = message.text.strip()
            task_info = get_task_by_pk(task_id)
            student_info = get_student_by_tg_id(message.from_user.id)
            if not task_info:
                bot.send_message(message.chat.id, "Вы ввели неправильный номер, попробуйте ещё раз:")
                bot.register_next_step_handler(message, process_get_task_id_from_student)
                return
            if task_info[5] == 0 or not (str(student_info[1]) in task_info[3] or task_info[3] == 'все'):
                bot.send_message(message.chat.id, "Вы ввели неправильный номер, попробуйте ещё раз:")
                bot.register_next_step_handler(message, process_get_task_id_from_student)
                return
            pdf_path_task = f"task/{task_info[1]}/{task_info[1]}_{student_info[2]}_{student_info[1]}.pdf"

            if os.path.exists(pdf_path_task):
                with open(pdf_path_task, "rb") as pdf1:
                    bot.send_document(message.chat.id, pdf1)
                bot.send_message(
                    message.chat.id,
                    f'Условие для {task_info[1]}\nДедлайн: {task_info[2]}', reply_markup = students_keyboard())
            else:
                bot.send_message(message.chat.id,
                                 f'Файл не найден. Проверьте, что ваше фио и группа записаны также, '
                                 f'как в списке лектора.',
                                 reply_markup = students_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в def process_get_task_id_from_student: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз позже.\n/start")
