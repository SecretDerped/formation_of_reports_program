import os
import sys
import json
import requests

from datetime import datetime

# Username пользователя
current_user = 'Antonette'

tasks_api_url = 'https://json.medrocket.ru/todos'
users_api_url = 'https://json.medrocket.ru/users'

# Формат даты для даты отчёта
date_format = '%Y-%m-%dT%H-%M'  # (2020-09-23T15-25)


# Возвращает данные из указанного URL
def getting_text_data_from_api(api_url):
    response = requests.get(api_url)
    data = json.loads(response.text)
    return data


# Если название задачи больше (length) символов,
# то сокращает название и добавляет заглушку (plug) в конец
def cutting_string(string):
    length = 48
    plug = '...'
    if len(string) > length:
        string = string[0: length] + plug
    return string


# Возвращает дату создания отчёта
def get_file_creation_time(target_file_name):
    with open(f'{target_file_name}', 'r', encoding='utf-8') as file:
        line = file.readlines()[1]
        date = line.split('>')[1]
        clear_date = date.strip()
    return clear_date


# Формирует и создаёт отчёты
def create_report(worker):
    # Получает список пользователей и ищет в нём нашего, собирая
    # его данные. Если пользователя нет, скрипт остановится
    users = getting_text_data_from_api(users_api_url)
    user_id_name = None
    user_full_name = None
    user_email = None
    user_company = None
    username_exists: bool = False

    for user in users:
        username = user.get('username')
        if worker == username:
            user_id_name = user.get('id')
            user_full_name = user.get('name')
            user_email = user.get('email')
            company_info = user.get('company')
            user_company = company_info.get('name')
            username_exists = True
    assert username_exists, 'Пользователь не найден. Проверьте правильность написания username, пожалуйста.'

    # Возвращает список задач, разбивает его на завершённые
    # и незавершённые
    tasks = getting_text_data_from_api(tasks_api_url)
    tasks_count = 0
    completed_tasks_list = []
    uncompleted_tasks_list = []

    for task in tasks:
        user_id = task.get('userId')
        if user_id == user_id_name:
            title = task.get('title')
            completed = task.get('completed')
            if completed:
                completed_tasks_list.append(cutting_string(title))
                tasks_count += 1
            else:
                uncompleted_tasks_list.append(cutting_string(title))
                tasks_count += 1

    # Если файл существует, меняет старому файлу имя,
    # при ошибке останавливает скрипт
    if os.path.isfile(f'{worker}.txt'):
        try:
            creation_time = get_file_creation_time(f'{worker}.txt')
            os.replace(f'{worker}.txt', f'old_{worker}_{creation_time}.txt')
        except OSError:
            print('Не удалось создать отчёт.')
            sys.exit(1)

    # Создаёт файл с отчётом
    with open(f'{worker}.txt', 'w', encoding='utf-8') as file:
        file_creation_time = datetime.now().strftime(date_format)
        file.write(f'Отчёт для {user_company}.\n'
                   f'{user_full_name} <{user_email}> {file_creation_time}\n'
                   f'\nВсего задач: {tasks_count}\n'
                   
                   '\nЗавершённые задачи:\n')
        for task in completed_tasks_list:
            file.write(task + '\n')
        file.write('\n\nОставшиеся задачи:\n')
        for task in uncompleted_tasks_list:
            file.write(task + '\n')


create_report(current_user)
