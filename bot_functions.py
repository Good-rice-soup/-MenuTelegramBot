import json  # нужна для адекватной работы с массивами при многопользовательском режиме
import sqlite3 as sq

import telebot
from telebot import types


class BotFunctions:

    # как-то там форматирует данные по образцу. через дебаг посмотри
    @staticmethod
    def format_templates(x):
        for j in range(len(x)):
            x[j] = list(x[j])

        a = []
        for j in range(len(x)):
            a.append(x[j][0])

        x = a.copy()
        a.clear()

        for i in range(len(x)):
            x[i] = x[i][:1].upper() + x[i][1:]

        return x

    # достаёт названия блюд с кавычками
    @staticmethod
    def get_special_names(x):
        with sq.connect("recipes.db") as con:
            cur = con.cursor()

            y = '"'
            cur.execute(
                f"SELECT name_of_dish FROM dishes WHERE name_of_dish like '%{y}%' AND name_of_dish like '%{x}%'")
            x = cur.fetchall()

            # форматирование данных по образцу
            x = BotFunctions.format_templates(x).copy()
            special_names = []
            for j in x:
                special_names.append(j.lower())

            special_names = ', '.join(special_names)

            return special_names

    # функция обрабатывает данные от пользователя, преобразуюя множество вариантов ввода в один конкретный запрос
    # также указывает, если названия в базе данных нет
    @staticmethod
    def get_search_request_func(x):
        a = ["блин", "заготовка", "каша", "крем-суп", "суп", "омлет", "салат", "соус", "тесто", "вафля"]
        b = ["Блин", "Заготовка", "Каша", "Крем-суп", "Крем-суп", "Омлет", "Салат", "Соус", "Тесто", "Вафля"]
        for i in range(len(a)):
            if a[i] in x:
                # получаем "особые" названия
                special_names = BotFunctions.get_special_names(b[i])
                search_request = ''.join(x.split(a[i])).strip()

                if search_request in special_names:
                    search_request = b[i] + ' "' + search_request[:1].upper() + search_request[1:]
                    return search_request
                else:
                    search_request = b[i] + ' ' + search_request
                    return search_request

        x = f'None - {x} - None'
        return x

    # ищет по запросу функции get_search_request_func(x) и выдаёт ответ на поиск
    @staticmethod
    def search_func(x):
        with sq.connect("recipes.db") as con:
            cur = con.cursor()
            cur.execute(f"SELECT name_of_dish, ingredients, comments FROM dishes WHERE name_of_dish like '%{x}%'")

            y = cur.fetchall()

            for j in range(len(y)):
                y[j] = list(y[j])

            if len(y) == 0:
                text = f"Такого блюда не нашлось в базе данных. Вот твой ввод: {x}. Возможно тут есть ошибки."
                return text

            elif len(y) > 1:
                text = f'По запросу "{x}" нашлось несколько блюд:\n'
                for i in range(len(y)):
                    text += f'{i + 1})' + y[i][0] + '\n'
                text += '\nНапиши цифру номера того блюда, которое тебе нужно. Да, просто 1 или 2, или что там написано.'
                return text

            text = ''
            a = y[0][1]
            a = a.split(', ')

            text += f"<b>{y[0][0]}</b>" + '\n'
            for i in range(len(a)):
                if i % 2 == 0:
                    text += f'{(i // 2) + 1})' + a[i][:1].upper() + a[i][1:] + ' - ' + a[i + 1] + ' гр/шт.\n'
            text += '\n<b>Комментарий:</b>\n' + y[0][2]

            return text

    # возвращает названия блюд, содержащих ингредиент
    @staticmethod
    def get_names_of_dishes(x):
        with sq.connect("recipes.db") as con:
            cur = con.cursor()

            cur.execute("SELECT name_of_dish FROM dishes_for_bot WHERE ingredients LIKE '%" + x + "%'")
            names = cur.fetchall()

            for j in range(len(names)):
                names[j] = list(names[j])

            a = []
            for j in range(len(names)):
                a.append(names[j][0])

            return a

    # выдаёт все ингридиенты из таблицы list_of_ingredients в виде массива
    @staticmethod
    def get_ingredients():
        with sq.connect("recipes.db") as con:
            cur = con.cursor()

            cur.execute("SELECT * FROM list_of_ingredients")
            ingredients_check_up = cur.fetchall()

            for j in range(len(ingredients_check_up)):
                ingredients_check_up[j] = list(ingredients_check_up[j])

            a = []
            for j in range(len(ingredients_check_up)):
                a.append(ingredients_check_up[j][0])

            return a

    # создаёт массив названий блюд и их ингридиентов без граммовок
    @staticmethod
    def get_dishes():
        with sq.connect("recipes.db") as con:
            cur = con.cursor()

            cur.execute("SELECT * FROM dishes_for_bot")
            dishes = cur.fetchall()

            for i in range(len(dishes)):
                dishes[i] = list(dishes[i])
                dishes[i][1] = dishes[i][1].split(', ')

            return dishes

    # там что-то как-то создаётся жёлтый список
    @staticmethod
    def get_yellow_list():
        global list_of_dishes
        global parameters
        dishes = BotFunctions.get_dishes()
        list_of_dishes = dishes.copy()

        yellow_dishes = []
        for i in range(len(dishes)):
            flag = 1
            counter = 0
            for k in range(len(dishes[i][1])):
                if dishes[i][1][k] in parameters[0]:
                    flag = 0
                if dishes[i][1][k] in parameters[1]:
                    counter += 1
            if flag and (not (counter == len(dishes[i][1]))):
                yellow_dishes.append(dishes[i])
        dishes.clear()

        return yellow_dishes

    # фукция применяет операцию strip() ко всем элементам массива
    @staticmethod
    def strip_func(array):
        for i in range(len(array)):
            array[i] = array[i].strip()

        return array

    # функция создания типовых кнопок для бота
    @staticmethod
    def markup_func(x):
        if x == 0:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton("Зелёный лист", callback_data='case_2')
            button_2 = types.InlineKeyboardButton("Жёлтый лист", callback_data='case_4')
            button_3 = types.InlineKeyboardButton("Стоп лист", callback_data='case_3')
            markup.row(button_1, button_2, button_3)
            return markup

        elif x == 1:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton("Зелёный лист", callback_data='case_2')
            button_2 = types.InlineKeyboardButton("Жёлтый лист", callback_data='case_4')
            button_3 = types.InlineKeyboardButton("Стоп лист", callback_data='case_3')
            button_4 = types.InlineKeyboardButton("Посчитать опять", callback_data='case_5')
            button_5 = types.InlineKeyboardButton('Вернуться в начало', callback_data="case_6")
            markup.row(button_1, button_2, button_3)
            markup.row(button_4, button_5)

            return markup

        elif x == 2:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton("Посчитать листы", callback_data='case_1')
            button_2 = types.InlineKeyboardButton('Помощь', callback_data='case_7')
            button_3 = types.InlineKeyboardButton('Поиск', callback_data='case_8')
            markup.row(button_1)
            markup.row(button_2, button_3)

            return markup

        elif x == 3:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton("Да, пожалуйста", callback_data='case_9')
            button_2 = types.InlineKeyboardButton('Нет, спасибо', callback_data='case_10')
            markup.row(button_1, button_2)

            return markup

        elif x == 4:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton('Вернуться в начало', callback_data="case_6")
            markup.row(button_1)

            return markup

        elif x == 5:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton("Ввести новые данные", callback_data='case_1')
            button_2 = types.InlineKeyboardButton('Не менять', callback_data='case_11')
            markup.row(button_1, button_2)

            return markup

        elif x == 6:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton('Вернуться в начало', callback_data="case_6")
            button_2 = types.InlineKeyboardButton('Как найти заготовки?', callback_data='case_12')
            markup.row(button_1, button_2)

            return markup

        elif x == 7:
            markup = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton("Да, пожалуйста", callback_data='case_13')
            button_2 = types.InlineKeyboardButton('Нет, спасибо', callback_data='case_10')
            button_3 = types.InlineKeyboardButton('Вернуться в начало', callback_data="case_6")
            markup.row(button_1, button_2)
            markup.row(button_3)

            return markup

    # выполняет запрос с использованием данных из нужных переменных
    @staticmethod
    def update_in_db(query, params=()):
        with sq.connect('users.db') as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()

    # функция обновления состояний на основании айди пользователя
    @staticmethod
    def select_from_db(params):
        global user_id
        global state
        global switch
        global yellow_list
        global green_list
        global stop_list
        global list_of_dishes
        global parameters
        global list_of_variants
        global list_of_outputs
        global iteration

        with sq.connect('users.db') as conn:
            cur = conn.cursor()
            print(params)
            cur.execute(f'SELECT * FROM user_data WHERE user_id == {params}')

            a = cur.fetchall()
            print(a)
            a = list(a[0])

        user_id = a[0]
        state = a[1]
        switch = a[2]
        yellow_list = json.loads(a[3])
        green_list = json.loads(a[4])
        stop_list = json.loads(a[5])
        list_of_dishes = json.loads(a[6])
        parameters = json.loads(a[7])
        list_of_variants = json.loads(a[8])
        list_of_outputs = json.loads(a[9])
        iteration = a[10]

    # получение переменных template и workpiece_template
    @staticmethod
    def db_connect():
        with sq.connect("recipes.db") as connect:
            cursor = connect.cursor()

            cursor.execute("SELECT * FROM list_of_ingredients")

            template = BotFunctions.format_templates(cursor.fetchall()).copy()
            template = ' - \n'.join(template) + ' - '

            cursor.execute("SELECT name_of_dish FROM dishes WHERE workpiece == 1")
            workpiece_template = BotFunctions.format_templates(cursor.fetchall())

            o = ''
            for p in range(len(workpiece_template)):
                o += f'{p + 1})' + workpiece_template[p] + '\n'
            workpiece_template = o


