import logging
import telebot
import os
from databases_methods.list_of_students_methods import get_students_by_group, get_unique_group_numbers
from databases_methods.students_methods import get_students_by_list_id
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

logging.basicConfig(
    filename = "bot_errors.log",
    level = logging.ERROR,
    format = "%(asctime)s - %(levelname)s - %(message)s",
)


def send_notification(task_info):
    try:
        group = task_info[3]
        if group.lower() == 'все':
            groups = get_unique_group_numbers()
        else:
            groups = group.split(", ")
        for group in groups:
            students_from_list = get_students_by_group(int(group))
            for one_student_from_list in students_from_list:
                students = get_students_by_list_id(one_student_from_list['id'])
                for student in students:
                    bot.send_message(student[0], f'Для вас доступно новое задание:\n'
                                                 f'Название: {task_info[1]}\n'
                                                 f'Дедлайн: {task_info[2]}')
                    pdf_path_task = f"task/{task_info[1]}/{task_info[1]}_{student[2]}_{student[1]}.pdf"

                    if os.path.exists(pdf_path_task):
                        with open(pdf_path_task, "rb") as pdf1:
                            bot.send_document(student[0], pdf1, caption = f'{task_info[1]}')
    except Exception as e:
        logging.error(f"Ошибка в send_notification: {e}")
