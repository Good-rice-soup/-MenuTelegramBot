import json  # нужна для адекватной работы с массивами при многопользовательском режиме
import sqlite3 as sq

import telebot
from telebot import types

# идея: сохранение ввода шаблона для списков для частичного редактирования\\потом

# глобальные переменные, важные для всех частей кода
user_id = 0
state = 0
switch = 0
yellow_list = []
green_list = []
stop_list = []
list_of_dishes = []
parameters = []
list_of_variants = []
list_of_outputs = []
iteration = 0

bot_API = ''
bot = telebot.TeleBot(bot_API)

# как-то там форматирует данные по образцу. через дебаг посмотри
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
def get_special_names(x):
    with sq.connect("recipes.db") as con:
        cur = con.cursor()

        y = '"'
        cur.execute(f"SELECT name_of_dish FROM dishes WHERE name_of_dish like '%{y}%' AND name_of_dish like '%{x}%'")
        x = cur.fetchall()

        # форматирование данных по образцу
        x = format_templates(x).copy()
        special_names = []
        for j in x:
            special_names.append(j.lower())

        special_names = ', '.join(special_names)

        return special_names


# функция обрабатывает данные от пользователя, преобразуюя множество вариантов ввода в один конкретный запрос
# также указывает, если названия в базе данных нет
def get_search_request_func(x):
    a = ["блин", "заготовка", "каша", "крем-суп", "суп", "омлет", "салат", "соус", "тесто", "вафля"]
    b = ["Блин", "Заготовка", "Каша", "Крем-суп", "Крем-суп", "Омлет", "Салат", "Соус", "Тесто", "Вафля"]
    for i in range(len(a)):
        if a[i] in x:
            # получаем "особые" названия
            special_names = get_special_names(b[i])
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
def get_yellow_list():
    global list_of_dishes
    global parameters
    dishes = get_dishes()
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
def strip_func(array):
    for i in range(len(array)):
        array[i] = array[i].strip()

    return array


# функция создания типовых кнопок для бота
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
def update_in_db(query, params=()):
    with sq.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()


# функция обновления состояний на основании айди пользователя
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
with sq.connect("recipes.db") as connect:
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM list_of_ingredients")

    template = format_templates(cursor.fetchall()).copy()
    template = ' - \n'.join(template) + ' - '

    cursor.execute("SELECT name_of_dish FROM dishes WHERE workpiece == 1")
    workpiece_template = format_templates(cursor.fetchall())

    o = ''
    for p in range(len(workpiece_template)):
        o += f'{p + 1})' + workpiece_template[p] + '\n'
    workpiece_template = o


# стартует бота
# тут происходит создание записи о пользователе, когда он приходит первый раз, обновление базовых состояний и тд
@bot.message_handler(commands=['start', '/start', 'Start'])
def start(message):
    global state
    state = 0
    _id = message.from_user.id

    # создание записи о новом пользователе
    with sq.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM user_data WHERE user_id == {_id}')
        result = cur.fetchall()

        if result:
            update_in_db("UPDATE user_data SET state = ? WHERE user_id = ?", (state, _id,))
        else:
            cur.execute(
                f"INSERT INTO user_data(user_id, state, switch, yellow_list, green_list, stop_list, list_of_dishes, "
                f"parameters, list_of_variants, list_of_outputs, iteration) VALUES "
                f"({_id}, 0, 0, '[]', '[]', '[]', '[]', '[]', '[]', '[]', 0)")

    # точка входа в бота
    markup = markup_func(2)
    bot.send_message(message.chat.id, 'Привет. Ты знаешь, зачем ты тут.', reply_markup=markup)


# тут обрабатываются все текстовые ответы от пользователя
@bot.message_handler(content_types=['text'])
def get_user_message(message):
    global state
    global parameters
    global template
    global list_of_variants
    global list_of_outputs
    global iteration

    # обновление состояний в зависимости от айди пользователя
    _id = message.from_user.id
    select_from_db(_id)

    # проверка нулевого состояния: защита от случайно введённого текста
    if state == 0:
        bot.send_message(message.chat.id, "Я тут не чтобы болтать с тобой. Используй кнопки или команды, либо вводи "
                                          "данные верно.")

    # проверка первого состояния: ввод шаблонов для создания листов
    elif state == 1:
        # взятие шаблона от пользователя
        parameters = message.text.strip().lower().split('\n')
        # функция введена для визуального уменьшения количества циклов
        parameters = strip_func(parameters).copy()

        # создание копии check_up в целях проверки, является ли введённый шаблон, для начала, шаблоном
        check_up = parameters.copy()
        # удалении пустых элементов, которые могли возникнуть при разбиении по '\n'
        while '' in check_up:
            check_up.remove('')

        # удаление 0 и 1 из ввода пользователя
        for i in range(len(check_up)):
            if check_up[i][-1].isdigit():
                check_up[i] = check_up[i][:len(check_up[i]) - 1]
            check_up[i] = check_up[i].strip()

        # обработка шаблонов для сравнения с вводом пользователя
        f = template.lower().split('\n')
        f = strip_func(f).copy()
        if '' in f:
            f.remove('')

        # сверка шаблона и ввода пользователя
        counter = 0
        for i in range(len(f)):
            if f[i] in check_up:
                counter += 1
        f.clear()

        flag = 1
        if counter != len(check_up):
            flag = 0

        if not flag:
            bot.send_message(message.chat.id, "Это неправильные данные. Ты ошибся где-то.")

        else:
            # повторная инициализация переменной check_up для сверки ответов от пользователя (1 и 0)
            check_up = parameters.copy()
            for i in range(len(check_up)):
                check_up[i] = check_up[i][len(check_up[i]) - 1:]

            # сверка
            mistakes = []
            flag = 1
            for i in range(len(check_up)):
                if check_up[i] not in '01':
                    flag = 0
                    mistakes.append(parameters[i])

            mistakes = '\n'.join(mistakes)

            if not flag:
                bot.send_message(message.chat.id, f"Данные верны, но я просил 1 или 0. Вот твои ошибки:\n\n{mistakes}")

            else:
                # обновление состояния, что значит завершение возможности ввода данных
                state = 0
                check_up.clear()

                # разбиение ввода на массив из пар: ингридиент и его состояние
                for i in range(len(parameters)):
                    if ' - ' in parameters[i]:
                        parameters[i] = parameters[i].lower().split(' - ')

                    elif ' -' in parameters[i]:
                        parameters[i] = parameters[i].lower().split(' -')

                    parameters[i].reverse()
                parameters.sort()

                # создание подмассивов наличия и не наличия ингридиентов
                a = []
                b = []
                for i in range(len(parameters)):
                    if parameters[i][0] == '0':
                        a.append(parameters[i][1])
                    else:
                        b.append(parameters[i][1])

                # получение итогового массва
                parameters.clear()
                parameters.append(a)
                parameters.append(b)

                markup = markup_func(0)
                bot.send_message(message.chat.id, "Понял тебя. Какой лист ты хочешь?",
                                 reply_markup=markup)

    # проверка второго состояния: ввод для поиска
    elif state == 2:
        # аналогичная состоянию 1 обработка
        request = message.text.strip().split('\n')
        request = strip_func(request).copy()
        while '' in request:
            request.remove('')

        # лист вариантов ответа на случай нескольких вариантов ответа при поиске:
        # блин с яйцом пашот и блин с яйцом пашот и салатом
        list_of_variants = []
        # текст сообщения вариантов для выбора (см далее для понимания)
        list_of_outputs = []
        # построчная обработка запроса
        for i in request:
            # проверка запроса. если есть *, то это поиск по тегу (ингридиенту)
            if i[:1] == '*':
                i = i[1:]
                # фича поиска по нескольким ингридиентам
                i = i.split(',')
                for j in range(len(i)):
                    i[j] = i[j].strip().lower()

                # получение массива с ингридиентами
                ingredients_check_up = get_ingredients().copy()
                flag = 0
                a = []
                # проверка на соответсвие ввода ингредиентам
                for j in range(len(i)):

                    if i[j] not in ingredients_check_up:
                        flag = 1
                        a.append(i[j])

                # возврат ошибок
                if flag:
                    text = 'В этих тегах есть какие-то ошибки:\n'
                    for j in a:
                        text += j + '\n'

                    markup = markup_func(4)
                    bot.send_message(message.chat.id, text, reply_markup=markup)

                else:
                    # создание списка блюд, включающих введённые теги
                    b = []
                    for j in i:
                        a = get_names_of_dishes(j).copy()
                        for k in a:
                            if k not in b:
                                b.append(k)
                        a.clear()
                    b.sort()

                    # вывод итогового результата
                    text = 'Ингредиенты (тэги) "' + ', '.join(i) + '" есть в следующих блюдах:\n'
                    for j in range(len(b)):
                        text += f"{j + 1})" + b[j] + '\n'

                    markup = markup_func(4)
                    bot.send_message(message.chat.id, text, reply_markup=markup)

            else:
                # обработка блюд и вывод их рецептов
                i = i.split(',')
                # фича множественного ввода
                for j in range(len(i)):
                    i[j] = i[j].strip().lower()

                for j in i:
                    # получение ответа на запрос
                    text = search_func(get_search_request_func(j))

                    # костыльный способ обработки исключения
                    if "По запросу" in text:

                        list_of_outputs.append(text)

                        # внесение конкретных вариантов в массив
                        text = text.split("\n")
                        u = []
                        for k in text:
                            if k[:1].isdigit():
                                u.append(k[2:])
                        list_of_variants.append(u)

                    else:
                        bot.send_message(message.chat.id, text, parse_mode='html')

        iteration = 0
        # проверка наличия нескольких вариантов ответа
        if len(list_of_variants) != 0:
            # регистрация следующего шага
            bot.register_next_step_handler(message, get_answer)
            bot.send_message(message.chat.id, list_of_outputs[iteration])

        else:
            markup = markup_func(4)
            bot.send_message(message.chat.id, 'Держи.\nЕсли надо найти что-то ещё, просто введи запрос, как до '
                                              'этого. Если нет, ты знашь, что делает эта кнопка.',
                             reply_markup=markup)

    # функция обновляет состояний конкретного пользователя
    update_in_db("UPDATE user_data SET state = ?, parameters = ?, list_of_variants = ?, list_of_outputs = ?, "
                 "iteration = ? WHERE user_id = ?",
                 (state, json.dumps(parameters), json.dumps(list_of_variants), json.dumps(list_of_outputs), iteration,
                  _id,))


# функция переспроса
def get_answer(message):
    global list_of_variants
    global list_of_outputs
    global iteration

    # обновление состояний по айди пользователя
    _id = message.from_user.id
    select_from_db(_id)

    # проверка на адекватность
    choice = message.text.strip()
    if not choice.isdigit():
        bot.send_message(message.chat.id, "Я просил цифру -_-")
        bot.register_next_step_handler(message, get_answer)

    else:
        # вторая проверка на адекватность
        if (int(choice) > len(list_of_variants[iteration])) or (int(choice) == 0):
            bot.send_message(message.chat.id, "Тут нет такого номера -_-")
            bot.register_next_step_handler(message, get_answer)

        else:
            # поиск по запросу
            with sq.connect("recipes.db") as con:
                cur = con.cursor()
                cur.execute(f"SELECT name_of_dish, ingredients, comments FROM dishes WHERE name_of_dish == "
                            f"'{list_of_variants[iteration][int(choice) - 1]}'")

                y = cur.fetchall()

            for j in range(len(y)):
                y[j] = list(y[j])

            text = ''
            a = y[0][1]
            a = a.split(', ')

            text += f"<b>{y[0][0]}</b>" + '\n'
            for i in range(len(a)):
                if i % 2 == 0:
                    text += f'{(i // 2) + 1})' + a[i][:1].upper() + a[i][1:] + ' - ' + a[i + 1] + ' гр/шт.\n'
            text += '\n<b>Комментарий:</b>\n' + y[0][2]

            bot.send_message(message.chat.id, text, parse_mode='html')

            # проверяем, все ли спорные блины мы уточнили
            if iteration != (len(list_of_outputs) - 1):
                iteration += 1
                bot.send_message(message.chat.id, list_of_outputs[iteration])
                bot.register_next_step_handler(message, get_answer)

            else:
                markup = markup_func(4)
                bot.send_message(message.chat.id, 'Держи.\nЕсли надо найти что-то ещё, просто введи запрос, как до '
                                                  'этого. Если нет, ты знашь, что делает эта кнопка.',
                                 reply_markup=markup)

    # обновление состояний
    update_in_db("UPDATE user_data SET list_of_variants = ?, list_of_outputs = ?, iteration = ? WHERE user_id = ?",
                 (json.dumps(list_of_variants), json.dumps(list_of_outputs), iteration, _id,))


# функция всех реакций через кнопки
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global parameters
    global workpiece_template
    global template
    global list_of_dishes
    global green_list
    global yellow_list
    global stop_list
    global state
    global switch

    # обновление состояний по айди пользователя
    _id = callback.from_user.id
    select_from_db(_id)

    # далее все возыращающиеся данные для удобства разбиты на кейсы
    if callback.data == "case_1":
        # кейс введения данных для списка

        if (parameters == []) or switch:
            # проверка на создание первых списков или их пересоздание

            if switch:
                # пересоздание списка, а точнее новый ввод данных для них
                green_list = []
                yellow_list = []
                stop_list = []
                parameters = []
                list_of_dishes = []
                switch = 0
                state = 1
                markup = markup_func(3)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id,
                                 "Хочешь сделать это опять? Окей, ты знаешь правила. Тебе нужен шаблон?",
                                 reply_markup=markup)

            else:
                # создание первого списка
                state = 1
                switch = 0
                markup = markup_func(3)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, "Пиши 1, если продукта достатоно, и 0, если нет. Пример:"
                                                           "\n\nОгурец маринованный - 1\nПомидор - 0\n\nТебе нужен "
                                                           "шаблон?", reply_markup=markup)

        else:
            # есть предыдущие данные, и мы хотим понять, что с ними делать
            state = 0
            switch = 1
            markup = markup_func(5)

            bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, 'У меня ещё есть предыдущие данные. Мне использовать их, или ты '
                                                       'дашь новые?', reply_markup=markup)

    elif callback.data == 'case_2':
        # кейс создания зелёного листа
        if not parameters:
            # обработка ошибки. после введения многопользовательского режма её появление возможно только при
            # повреждении базы данных
            state = 1

            bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, "Я не могу это сделать, так как у меня нет данных (возможно "
                                                       "что-то случилось на сервере и я забыл их). Отправь их ещё раз, "
                                                       "пожалуйста.")
        else:
            if not green_list:
                # проверка существования зелёного листа

                bot.send_message(callback.message.chat.id,
                                 "-----------------------------------------------------------")

                # проверка существования массива блюд
                if not list_of_dishes:
                    list_of_dishes = get_dishes()

                # создание зелёного листа на основе ввода пользователя
                green_list = []
                for i in range(len(list_of_dishes)):
                    flag = 1
                    for k in range(len(list_of_dishes[i][1])):
                        if list_of_dishes[i][1][k] not in parameters[1]:
                            flag = 0
                    if flag:
                        green_list.append(list_of_dishes[i])

                # преобразование в текст
                text = '🟩 Зелёный лист:\n'
                green_list.sort()
                for i in range(len(green_list)):
                    text += f'{i + 1})' + green_list[i][0] + '.\n'

                markup = markup_func(1)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, text, reply_markup=markup)

            else:
                # если зелёный лист есть, просто выводим его
                bot.send_message(callback.message.chat.id,
                                 "-----------------------------------------------------------")

                text = '🟩 Зелёный лист:\n'
                green_list.sort()
                for i in range(len(green_list)):
                    text += f'{i + 1})' + green_list[i][0] + '.\n'

                markup = markup_func(1)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, text, reply_markup=markup)

    elif callback.data == 'case_3':
        # кейс создания стоп листа

        if not parameters:
            # обработка аналогичная второму кейсу
            state = 1

            bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, "Я не могу это сделать, так как у меня нет данных (возможно "
                                                       "что-то случилось на сервере и я забыл их). Отправь их ещё раз, "
                                                       "пожалуйста.")
        else:
            if not stop_list:
                # аналогичная проверка всего, как и во втором кейсе

                bot.send_message(callback.message.chat.id,
                                 "-----------------------------------------------------------")

                if not list_of_dishes:
                    list_of_dishes = get_dishes()

                stop_list = []
                for i in range(len(list_of_dishes)):
                    flag = 0
                    for k in range(len(list_of_dishes[i][1])):
                        if list_of_dishes[i][1][k] in parameters[0]:
                            flag = 1
                    if flag:
                        stop_list.append(list_of_dishes[i])

                text = '🟥 Стоп лист:\n'
                stop_list.sort()
                for i in range(len(stop_list)):
                    text += f'{i + 1})' + stop_list[i][0] + '.\n'

                markup = markup_func(1)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, text, reply_markup=markup)

            else:
                # вывод стоп листа, если он есть
                bot.send_message(callback.message.chat.id,
                                 "-----------------------------------------------------------")

                text = '🟥 Стоп лист:\n'
                stop_list.sort()
                for i in range(len(stop_list)):
                    text += f'{i + 1})' + stop_list[i][0] + '.\n'

                markup = markup_func(1)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, text, reply_markup=markup)

    elif callback.data == 'case_4':
        # кейс создания жёлтого листа
        if not parameters:
            # всё то же самое
            state = 1

            bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
            bot.send_message(callback.message.chat.id, "Я не могу это сделать, так как у меня нет данных (возможно "
                                                       "что-то случилось на сервере и я забыл их). Отправь их ещё раз, "
                                                       "пожалуйста.")
        else:
            if not yellow_list:

                bot.send_message(callback.message.chat.id,
                                 "-----------------------------------------------------------")

                # создание жёлтого листа в функции
                a = get_yellow_list()
                yellow_list = a.copy()
                a.clear()

                text = '🟨 Жёлтый лист:\n'
                yellow_list.sort()
                for i in range(len(yellow_list)):
                    text += f'{i + 1})' + yellow_list[i][0] + '.\n'

                markup = markup_func(1)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, text, reply_markup=markup)

            else:
                # если лист есть, просто выводим
                bot.send_message(callback.message.chat.id,
                                 "-----------------------------------------------------------")

                text = '🟨 Жёлтый лист:\n'
                yellow_list.sort()
                for i in range(len(yellow_list)):
                    text += f'{i + 1})' + yellow_list[i][0] + '.\n'

                markup = markup_func(1)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, text, reply_markup=markup)

    elif callback.data == 'case_5':
        # кейс подсчёта листов заново

        bot.send_message(callback.message.chat.id, "-----------------------------------------------------------")

        green_list = []
        yellow_list = []
        stop_list = []
        parameters = []
        list_of_dishes = []
        state = 1
        markup = markup_func(3)

        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Хочешь сделать это опять? Окей, ты знаешь правила. Тебе нужен "
                                                   "шаблон?", reply_markup=markup)

    elif callback.data == 'case_6':
        # кейс "нового старта"
        bot.send_message(callback.message.chat.id, "-----------------------------------------------------------")

        state = 0
        markup = markup_func(2)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Привет, ты знаешь, зачем ты тут.', reply_markup=markup)

    elif callback.data == 'case_7':
        # кейс помощи
        bot.send_message(callback.message.chat.id, "-----------------------------------------------------------")

        markup = markup_func(4)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, '<b>Поиск</b>\n'
                                                   'Поиск возможно сделать двумя способами:\n1)По ингридиенту (тегу).\n'
                                                   '2)По названию блинчика.\n\nПример:\nПри вводе ингридиента сначала '
                                                   'надо поставить знак "*" перед ингридиентом: *ветчина. Тогда поиск '
                                                   'выдаст все блинчики, которые содержат ингридиент (тег) "ветчина". '
                                                   'Однако, можно ввести и серию тегов через запятую: *ветчина, гауда и'
                                                   ' тд.\n\nТакже можно ввести и название блина (полностью или частично'
                                                   '), и тогда будет выведен соответсвующий состав с граммами '
                                                   'ингридиентов.\n\n<b>Подстёт продуктов</b>\nЭта функция '
                                                   'позволяет создавать зелёные, жёлтые и стоп листы.\n\nЗелёный лист -'
                                                   ' блюда, которые точно можно приготовить на основании введённых '
                                                   'ингридиентов.\n\nСтоп лист - блюда, которые точно нельзя '
                                                   'приготовить на основании введённых ингридиентов.\n\nЖелтый лист - '
                                                   'блюда, для определения статуса которых не хватает данных.\n\n'
                                                   'Подсказка: присылаемый шаблон достаточно удобно скопировать и '
                                                   'дальше просто заполнить (собственно говоря, в этом и заключается '
                                                   'идея).\n\n<b>Наставления</b>\n'
                                                   'Также очевидно, что не стоит лишний раз ошибаться '
                                                   'при написании слов, или использовании шаблонов, так как '
                                                   'предугадывание потенциальных описок у пользователя значительно '
                                                   'усложняет логику работы бота, увеличивает время обработки запроса и'
                                                   ' количество потенциальных ошибок в коде проекта. Так что пишите, '
                                                   'пожалуйста, так, как просят в образце. Тем не менее, некоторый '
                                                   '"запас прочности" в распознавании ошибок был заложен в бота, но не '
                                                   'стоит всецело полагаться на него.',
                         parse_mode='html', reply_markup=markup)

    elif callback.data == 'case_8':
        # кейс поиска
        bot.send_message(callback.message.chat.id, "-----------------------------------------------------------")
        state = 2

        markup = markup_func(6)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Введитет ингридиент (тег) или название блинчика.',
                         reply_markup=markup)

    elif callback.data == 'case_9':
        # кейс отправки шаблона
        markup = markup_func(4)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, template, reply_markup=markup)

    elif callback.data == 'case_10':
        # кейс ответа на отказ от шаблона
        markup = markup_func(4)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Окей, как знаешь.", reply_markup=markup)

    elif callback.data == 'case_11':
        # кейс выбора первого листа для печати
        switch = 0
        markup = markup_func(0)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Понял тебя. Какой лист тебе нужен?",
                         reply_markup=markup)

    elif callback.data == 'case_12':
        # кейс "помощи" к поиску
        markup = markup_func(7)
        bot.send_message(callback.message.chat.id, "Чтобы найти заготовку, просто введи её название (всё точно также, "
                                                   "как и с блинами). Тебе нужен список заготовок?",
                         reply_markup=markup)

    elif callback.data == 'case_13':
        # кейс с шаблоном заготовок
        markup = markup_func(4)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, workpiece_template, reply_markup=markup)

    # обновление базы данных
    update_in_db("UPDATE user_data SET state = ?, switch = ?, yellow_list = ?, green_list = ?, stop_list = ?, "
                 "list_of_dishes = ?, parameters = ?, list_of_variants = ?, list_of_outputs = ?, iteration = ? "
                 "WHERE user_id = ?",
                 (state, switch, json.dumps(yellow_list), json.dumps(green_list), json.dumps(stop_list),
                  json.dumps(list_of_dishes), json.dumps(parameters), json.dumps(list_of_variants),
                  json.dumps(list_of_outputs), iteration, _id,))


# бесконечная работа бота
bot.polling(none_stop=True)