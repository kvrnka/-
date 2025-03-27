import logging
from telebot import types
import os
from databases_methods.admins_methods import get_all_admin, delete_admin_by_username
from databases_methods.list_of_students_methods import (add_by_excel, get_list_of_students, add_student_in_list,
                                                        delete_student_from_list)
from databases_methods.key_for_admin import add_key


logging.basicConfig(
    filename="bot_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# клавиатурка
def main_admin_keyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Изменить список студентов', callback_data = 'edit_list_of_students'))
        markup.add(types.InlineKeyboardButton('Просмотр администраторов', callback_data = 'list_of_admin'))
        markup.add(
            types.InlineKeyboardButton('Создать новую работу', callback_data = 'create_task'))
        markup.add(
            types.InlineKeyboardButton('Просмотр заданий', callback_data = 'list_of_task'))
        return markup



def setup_main_admin_handlers(bot):
    # просмотр администраторов
    @bot.callback_query_handler(func = lambda callback: callback.data in ['list_of_admin'])
    def get_list_of_admin(callback):
        try:
            admins = get_all_admin()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Добавить новых администраторов', callback_data = 'add_new_admin'))
            markup.add(types.InlineKeyboardButton('Удалить администратора', callback_data = 'delete_admin'))
            if not admins:
                bot.send_message(callback.message.chat.id, f"Список администраторов пуст.",
                                 reply_markup = markup)
            else:
                bot.send_message(callback.message.chat.id, f"Список администраторов: \n"
                                                           f"{admins}"
                                                           f"Выберите следующее действие:", reply_markup = markup)
        except Exception as e:
            logging.error(f"Ошибка в команде get_list_of_admin: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз позже.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['add_new_admin', 'delete_admin'])
    def change_admins(callback):
        try:
            if callback.data == 'add_new_admin':
                bot.send_message(callback.message.chat.id,
                                 f"Чтобы добавить новых администраторов, вам нужно создать пароль, который будет действовать 48ч. "
                                 f"Выдайте этот пароль людям, которые должны зарегистрироваться, как администраторы. \n"
                                 f"Введите пароль:")
                bot.register_next_step_handler(callback.message, process_create_password)
            else:
                bot.send_message(callback.message.chat.id,
                                 f"Введите телеграм ник администратора без знака '@', которого хотите удалить. "
                                 f"Если хотите удалить несколько администраторов, введите их ники через запятую.\n"
                                 f"Например: petrov, ivanov, sidorov")
                bot.register_next_step_handler(callback.message, process_delete_admin)
        except Exception as e:
            logging.error(f"Ошибка в change_admins: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз позже.")

    def process_create_password(message):
        try:
            password = message.text
            tg_id = message.from_user.id
            add_key(tg_id, password)
            bot.send_message(message.chat.id, f"Пароль сохранен!")
        except Exception as e:
            logging.error(f"Ошибка в process_create_password: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз ввести пароль.")

    def process_delete_admin(message):
        try:
            tg_nik = message.text
            check = delete_admin_by_username(tg_nik)
            new_list = get_all_admin()
            if check:
                if new_list:
                    bot.send_message(message.chat.id,
                                     f"Пользователи успешно удалены из администраторов. Новый список администраторов:\n"
                                     f"{new_list}", reply_markup = main_admin_keyboard())
                else:
                    bot.send_message(message.chat.id,
                                     f"Пользователи успешно удалены из администраторов. Теперь список администраторов пуст.",
                                     reply_markup = main_admin_keyboard())
            else:
                bot.send_message(message.chat.id,
                                 f"Не удалось удалить какого-то пользователя из администраторов. Список на данный момент: \n"
                                 f"{new_list}", reply_markup = main_admin_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_delete_admin: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['edit_list_of_students'])
    def change_list_of_students(callback):
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Создать новый список', callback_data = 'new_list_of_students'))
            markup.add(types.InlineKeyboardButton('Редактировать список', callback_data = 'add_or_delete_student'))
            bot.send_message(callback.message.chat.id, f"Выберите следующее действие: \n"
                                                       f'При выборе "Создать новый список" старый список удалится',
                             reply_markup = markup)
        except Exception as e:
            logging.error(f"Ошибка в change_list_of_students: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['add_or_delete_student'])
    def edit_list_of_students(callback):
        try:
            list_of_students = get_list_of_students()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Добавить студента', callback_data = 'add_new_student'))
            markup.add(types.InlineKeyboardButton('Удалить студентов', callback_data = 'delete_old_students'))
            bot.send_message(callback.message.chat.id, f"Список студентов: \n"
                                                       f"{list_of_students}\n"
                                                       f"Выберите действие:", reply_markup = markup)
        except Exception as e:
            logging.error(f"Ошибка в edit_list_of_students: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['add_new_student', 'delete_old_students'])
    def change_handler(callback):
        try:
            if callback.data == 'add_new_student':
                bot.send_message(callback.message.chat.id,
                                 f"Введите имя и группу студента через запятую. \n"
                                 f"Если вы хотите внести в список сразу несколько студентов, то каждого студента записывайте с новой строки. \n"
                                 f"Например: \nИванов Иван, 235\n Петров Петр, 236\n Светланова Светлана, 234")
                bot.register_next_step_handler(callback.message, process_name_of_new_student)
            else:
                bot.send_message(callback.message.chat.id,
                                 f"Введите номера студентов, которых хотите удалить, через запятую и пробел. Например: 1, 4, 6")
                bot.register_next_step_handler(callback.message, process_delete_students)
        except Exception as e:
            logging.error(f"Ошибка в change_handler: {e}")
            bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    def process_name_of_new_student(message):
        try:
            str = message.text
            add_student_in_list(str)
            list_of_students = get_list_of_students()
            bot.send_message(message.chat.id, f"Список изменён:\n"
                                              f"{list_of_students}"
                                              f"Выберите следующее действие:", reply_markup = main_admin_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_name_of_new_student: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    def process_delete_students(message):
        try:
            numbers = message.text
            if delete_student_from_list(numbers):
                list_of_students = get_list_of_students()
                bot.send_message(message.chat.id, f"Все выбранные студенты удалены, обновленный список:\n"
                                                  f"{list_of_students}"
                                                  f"Выберите следующее действие:", reply_markup = main_admin_keyboard())
            else:
                list_of_students = get_list_of_students()
                bot.send_message(message.chat.id, f"Не удалось удалить студента, список на данный момент:\n"
                                                  f"{list_of_students}"
                                                  f"Выберите следующее действие:", reply_markup = main_admin_keyboard())
        except Exception as e:
            logging.error(f"Ошибка в process_delete_students: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    @bot.callback_query_handler(func = lambda callback: callback.data in ['new_list_of_students'])
    def new_list_of_students(callback):
        bot.send_message(callback.message.chat.id,
                         "Пришлите файл со списком студентов в формате, сделанный по следующим правилам:\n"
                         "1) Формат файла: .xlsx или .xls \n"
                         '2) Таблица должна содержать два столбца: имена студентов (этот столбец должен иметь название "full_name"), номер группы (столбец должен называться "group_number")')

    @bot.message_handler(content_types = ['document'])
    def handle_document(message):
        try:
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            file_path = file_info.file_path

            downloaded_file = bot.download_file(file_path)
            local_filename = f"temp_{message.document.file_name}"

            if not (local_filename.endswith('.xlsx') or local_filename.endswith('.xls')):
                bot.send_message(message.chat.id, "Ошибка! Отправьте файл в формате Excel (.xlsx или .xls).")
                return

            with open(local_filename, "wb") as new_file:
                new_file.write(downloaded_file)

            response = add_by_excel(local_filename)

            os.remove(local_filename)

            list_of_students = get_list_of_students()
            text = response + '\n' + list_of_students
            bot.send_message(message.chat.id, text)
        except Exception as e:
            logging.error(f"Ошибка в handle_document: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка! Попробуйте еще раз.")

    # @bot.callback_query_handler(func = lambda callback: callback.data in ['create_task'])
    # def create_task(callback):
    #     try:
    #         bot.send_message(callback.message.chat.id, f"Введите название новой работы")
    #         bot.register_next_step_handler(callback.message, process_name_of_new_task)
    #     except Exception as e:
    #         logging.error(f"Ошибка в create_task: {e}")
    #         bot.send_message(callback.message.chat.id, "Произошла ошибка! Попробуйте еще раз.")
    #
    #
    # def process_name_of_new_task(message):
    #     name = message.text


    @bot.callback_query_handler(func = lambda callback: callback.data in ['list_of_task'])
    def get_list_of_task(callback):
        pass
