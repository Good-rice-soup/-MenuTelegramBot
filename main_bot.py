import json  # нужна для адекватной работы с массивами при многопользовательском режиме
import sqlite3 as sq

import bot_functions as bt

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
            bt.update_in_db("UPDATE user_data SET state = ? WHERE user_id = ?", (state, _id,))
        else:
            cur.execute(
                f"INSERT INTO user_data(user_id, state, switch, yellow_list, green_list, stop_list, list_of_dishes, "
                f"parameters, list_of_variants, list_of_outputs, iteration) VALUES "
                f"({_id}, 0, 0, '[]', '[]', '[]', '[]', '[]', '[]', '[]', 0)")

    # точка входа в бота
    markup = bt.markup_func(2)
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
    bt.select_from_db(_id)

    # проверка нулевого состояния: защита от случайно введённого текста
    if state == 0:
        bot.send_message(message.chat.id, "Я тут не чтобы болтать с тобой. Используй кнопки или команды, либо вводи "
                                          "данные верно.")

    # проверка первого состояния: ввод шаблонов для создания листов
    elif state == 1:
        # взятие шаблона от пользователя
        parameters = message.text.strip().lower().split('\n')
        # функция введена для визуального уменьшения количества циклов
        parameters = bt.strip_func(parameters).copy()

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
        f = bt.strip_func(f).copy()
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

                markup = bt.markup_func(0)
                bot.send_message(message.chat.id, "Понял тебя. Какой лист ты хочешь?",
                                 reply_markup=markup)

    # проверка второго состояния: ввод для поиска
    elif state == 2:
        # аналогичная состоянию 1 обработка
        request = message.text.strip().split('\n')
        request = bt.strip_func(request).copy()
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
                ingredients_check_up = bt.get_ingredients().copy()
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

                    markup = bt.markup_func(4)
                    bot.send_message(message.chat.id, text, reply_markup=markup)

                else:
                    # создание списка блюд, включающих введённые теги
                    b = []
                    for j in i:
                        a = bt.get_names_of_dishes(j).copy()
                        for k in a:
                            if k not in b:
                                b.append(k)
                        a.clear()
                    b.sort()

                    # вывод итогового результата
                    text = 'Ингредиенты (тэги) "' + ', '.join(i) + '" есть в следующих блюдах:\n'
                    for j in range(len(b)):
                        text += f"{j + 1})" + b[j] + '\n'

                    markup = bt.markup_func(4)
                    bot.send_message(message.chat.id, text, reply_markup=markup)

            else:
                # обработка блюд и вывод их рецептов
                i = i.split(',')
                # фича множественного ввода
                for j in range(len(i)):
                    i[j] = i[j].strip().lower()

                for j in i:
                    # получение ответа на запрос
                    text = bt.search_func(bt.get_search_request_func(j))

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
            markup = bt.markup_func(4)
            bot.send_message(message.chat.id, 'Держи.\nЕсли надо найти что-то ещё, просто введи запрос, как до '
                                              'этого. Если нет, ты знашь, что делает эта кнопка.',
                             reply_markup=markup)

    # функция обновляет состояний конкретного пользователя
    bt.update_in_db("UPDATE user_data SET state = ?, parameters = ?, list_of_variants = ?, list_of_outputs = ?, "
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
    bt.select_from_db(_id)

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
                markup = bt.markup_func(4)
                bot.send_message(message.chat.id, 'Держи.\nЕсли надо найти что-то ещё, просто введи запрос, как до '
                                                  'этого. Если нет, ты знашь, что делает эта кнопка.',
                                 reply_markup=markup)

    # обновление состояний
    bt.update_in_db("UPDATE user_data SET list_of_variants = ?, list_of_outputs = ?, iteration = ? WHERE user_id = ?",
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
    bt.select_from_db(_id)

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
                markup = bt.markup_func(3)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id,
                                 "Хочешь сделать это опять? Окей, ты знаешь правила. Тебе нужен шаблон?",
                                 reply_markup=markup)

            else:
                # создание первого списка
                state = 1
                switch = 0
                markup = bt.markup_func(3)

                bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
                bot.send_message(callback.message.chat.id, "Пиши 1, если продукта достатоно, и 0, если нет. Пример:"
                                                           "\n\nОгурец маринованный - 1\nПомидор - 0\n\nТебе нужен "
                                                           "шаблон?", reply_markup=markup)

        else:
            # есть предыдущие данные, и мы хотим понять, что с ними делать
            state = 0
            switch = 1
            markup = bt.markup_func(5)

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
                    list_of_dishes = bt.get_dishes()

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

                markup = bt.markup_func(1)

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

                markup = bt.markup_func(1)

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
                    list_of_dishes = bt.get_dishes()

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

                markup = bt.markup_func(1)

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

                markup = bt.markup_func(1)

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
                a = bt.get_yellow_list()
                yellow_list = a.copy()
                a.clear()

                text = '🟨 Жёлтый лист:\n'
                yellow_list.sort()
                for i in range(len(yellow_list)):
                    text += f'{i + 1})' + yellow_list[i][0] + '.\n'

                markup = bt.markup_func(1)

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

                markup = bt.markup_func(1)

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
        markup = bt.markup_func(3)

        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Хочешь сделать это опять? Окей, ты знаешь правила. Тебе нужен "
                                                   "шаблон?", reply_markup=markup)

    elif callback.data == 'case_6':
        # кейс "нового старта"
        bot.send_message(callback.message.chat.id, "-----------------------------------------------------------")

        state = 0
        markup = bt.markup_func(2)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Привет, ты знаешь, зачем ты тут.', reply_markup=markup)

    elif callback.data == 'case_7':
        # кейс помощи
        bot.send_message(callback.message.chat.id, "-----------------------------------------------------------")

        markup = bt.markup_func(4)
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

        markup = bt.markup_func(6)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, 'Введитет ингридиент (тег) или название блинчика.',
                         reply_markup=markup)

    elif callback.data == 'case_9':
        # кейс отправки шаблона
        markup = bt.markup_func(4)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, template, reply_markup=markup)

    elif callback.data == 'case_10':
        # кейс ответа на отказ от шаблона
        markup = bt.markup_func(4)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Окей, как знаешь.", reply_markup=markup)

    elif callback.data == 'case_11':
        # кейс выбора первого листа для печати
        switch = 0
        markup = bt.markup_func(0)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, "Понял тебя. Какой лист тебе нужен?",
                         reply_markup=markup)

    elif callback.data == 'case_12':
        # кейс "помощи" к поиску
        markup = bt.markup_func(7)
        bot.send_message(callback.message.chat.id, "Чтобы найти заготовку, просто введи её название (всё точно также, "
                                                   "как и с блинами). Тебе нужен список заготовок?",
                         reply_markup=markup)

    elif callback.data == 'case_13':
        # кейс с шаблоном заготовок
        markup = bt.markup_func(4)
        bot.edit_message_text(callback.message.text, callback.message.chat.id, callback.message.message_id)
        bot.send_message(callback.message.chat.id, workpiece_template, reply_markup=markup)

    # обновление базы данных
    bt.update_in_db("UPDATE user_data SET state = ?, switch = ?, yellow_list = ?, green_list = ?, stop_list = ?, "
                 "list_of_dishes = ?, parameters = ?, list_of_variants = ?, list_of_outputs = ?, iteration = ? "
                 "WHERE user_id = ?",
                 (state, switch, json.dumps(yellow_list), json.dumps(green_list), json.dumps(stop_list),
                  json.dumps(list_of_dishes), json.dumps(parameters), json.dumps(list_of_variants),
                  json.dumps(list_of_outputs), iteration, _id,))


# бесконечная работа бота
bot.polling(none_stop=True)