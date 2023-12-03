# -MenuTelegramBot

Table of contents:

[ENG](#overview)

[RU](#обзор)

## Overview:

This bot is designed to search for dishes in a database that can be prepared based on a given set of ingredients, create stop lists (red lists), waiting lists (yellow lists), and available for cooking lists (green lists), as well as search for recipes for preparing dishes. The bot supports multi-user mode. This bot comes with a database of dishes, a database for working in multi-user mode, a script for converting the database into a .tex document, custom scripts for working with the database.

!!! Working with the Bot: After launching the bot, the user is presented with three commands:

Calculate Lists

Request Help

Perform a Database Search

When calculating lists, if the bot has previously saved user-entered data, it will suggest using them and skip the procedure of entering new data. If this option is chosen, the bot will immediately suggest moving on to creating green, yellow, and red lists. Otherwise, the bot will suggest sending a message with the rules of filling out (0 - no ingredient; 1 - ingredient is present) and suggest sending a template containing all the ingredients from all the dishes. The user can respond to the bot's proposal with agreement or refusal, or simply ignore it. This will NOT break the bot.

IMPORTANT: When filling out the template, it is important to follow the syntax "Cucumber - 1". The bot includes some protection against typos, and if you enter "Cucumber -1", "CUCUMBER - 1" or "CUCUMBER -1", nothing serious will happen, but the author strongly advises against doing so. The bot also includes some input data validation: if you enter a random set of characters or just "Cucumber," you will receive a message that the data is incorrect, and if you enter "Cucumber -," the bot will inform you that it expects values of 0 or 1 and specify the specific ingredients where you need to enter them. After receiving an error message, you do not need to exit the menu and start entering ingredients from scratch. Simply resend the corrected message.

After that, you will have the option to calculate the following lists:

Red List (stop list) contains all the dishes that lack at least one ingredient, preventing the workpiece of the dish. Green List (available for cooking list) contains all the dishes for which the ingredients are definitely available. Yellow List (waiting list) contains all other dishes for which there is insufficient information to classify them as red or green. The bot will also offer you the option to return to the main menu and calculate the lists again. When choosing to recalculate the lists, everything described earlier will be repeated, but without the possibility to use previously entered data. In addition, during the data input process, the bot will suggest going back if you accidentally initiated this function.

The "Help" command will provide a brief instruction on how to use the bot and then offer you to return to the beginning.

The "Search" command offers two search options:

1)By ingredient.

2)By dish name.

The first option is executed by sending a message with the following syntax: "*ingredient_1" or "*ingredient_1, ingredient_2." In the first case, all dishes containing ingredient_1 will be displayed, and in the second case, all dishes containing either ingredient_1 OR ingredient_2 will be displayed. The number of ingredients in this sequence is not limited. In case of entering an incorrect ingredient, the bot will notify you.

The second option assumes that you will enter the full or partial name of a dish. Suppose we have dishes "pancake 1" and "pancake 12". If we enter "pancake 1," the bot will send us a message with a numbered list of "namesakes" and ask us to enter ONLY the number of the specific dish. If you enter a letter instead of a number, the bot will say it requested a digit, and if you enter an incorrect number, it will tell you that there is no such number. In the process, the bot will offer to return to the main menu and wait for you to enter the correct number. After entering the correct number, the bot will send us the technical card for the desired pancake. If you enter non-existent dishes, the bot will notify you that there is no such dish in the database.

At the beginning of the search, the bot optionally offers to show the list of blanks.

!!! Dish Database: This database contains three main tables: dishes, bot dishes, and a list of ingredients.

In the "Dishes" table, there are the following fields:

Dish Name
Ingredients
Comments
Workpiece
The "Dish Name" field contains a string. Since the bot's search algorithm and the algorithm for creating a technical card for chefs imply orientation to the "class" of the dish, it is necessary to include this information before the dish name. For example: "soup 'solyanka'," "oatmeal porridge," "pancake with salmon," and so on. The corresponding classes are specified in the bot's code in the function "get_search_request_func(x)," so if the number of classes in the database changes, they will need to be updated there.

The "Ingredients" field contains a string. Information is recorded as follows: "ingredient, quantity, ingredient, quantity." It is important to maintain the separator ", " or it will break the bot. The quantity is entered in grams (only digits) or sometimes in pieces (context-dependent).

The "Comments" field contains a string with explanations for workpiece.

The "Workpiece" field contains a value of 0 or 1. 1 - this dish is a workpiece, 0 - the opposite of 1.

In the "Bot Dishes" table, there are the following fields:

Dish Name
Ingredients
The rules for this table are absolutely the same as for the previous one. This table was created to facilitate the writing and testing of the bot, but it can be removed if necessary (after modifying the corresponding element in the code) and replaced with the "Dishes" table. The main difference is that there are no gram measurements in the "Ingredients" column because this table was used for creating red, yellow, and green lists, not for searching for recipes and creating technical cards. If you encounter any issues with this table, run custom scripts for the database, and everything will be fixed.

In the "List of Ingredients" table, there is the following field:

Ingredient.
This field contains the name of a single ingredient (workpieces can also be ingredients).

!!! User Database: The user database includes the following fields: "user_id" INTEGER, "state" INTEGER, "switch" INTEGER, "yellow_list" TEXT, "green_list" TEXT, "stop_list" TEXT, "list_of_dishes" TEXT, "parameters" TEXT, "list_of_variants" TEXT, "list_of_outputs" TEXT, "iteration" INTEGER. All fields except "user_id" are global variables because this field represents the user's ID in Telegram.

Script for Conversion to a .tex Document: Based on the dish database, the script creates a document with a .tex extension, allowing for easy conversion of the database into convenient technical cards for chefs using LaTeX. All the necessary libraries for successful compilation are preselected and included in the final file, so all you need to do is open the generated document in LaTeX and start the compilation process. The document is sorted by dish categories (see the dish database) and alphabetically line by line.

Custom Scripts: Upon opening the document, there is a request to update/create a database dump (with protection against mistakes), after which the dishes and workpieces are resorted alphabetically, ingredient lists and lists of dishes for the bot are updated (see the dish database).


## Обзор:
Этот чат-бот создан для облегчения работы повара. Среди возможностей бота есть:
- [Создание стоп листов и не только на основании наличия ингредиентов](#создание-списков-блюд)
- [Поиск блюд, содержащих ингредиент по списку ингредиентов, вывод технологических карт блюд](#команда-"поиск")
- [Печать технологической карты в формате LaTex](#4.-скрипт-перевода-в-.tex-документ)

### 1. Работа с ботом: 
Доступный функционал:
- [Создание списков блюд (листов)](#создание-списков-блюд)
  - Красные
  - Жёлтые
  - Зелёные
- [Команда "Помощь"](#команда-помощь)
- [Поиск блюд по списку ингридиентов](#команда-поиск)
- [Запрос технологической карты по названию блюда](#команда-поиск)

#### Создание списков блюд:
Данный бот поддерживает несколько вариантов списков (листов) блюд:
- Красный лист - стоп лист. Содержит все блюда, для которых известно, что не хватает хотя бы одного ингредиента.
- Жёлтый лист - лист ожидания. Содержит все блюда, о которых недостаточно информации для записи в красный или зелёный лист.
- Зелёный лист - лист "Доступно к приготовлению". Содержит все блюда, ингредиенты для которых точно есть.

Бот умеет сохранять данные из предыдущего ввода пользователя. При их наличии бот преложит использовать их и пропустить процецуру ввода новых. Если выбрать этот вариант, бот сразу перейдёт к созданию списков. 

В случае отказа от использования старых данных, бот отправит сообщение с правилами заполнения (0 -ингредиента нет; 1 - ингредиент есть) и прделожение прислать шаблон, содержащий все ингредиенты всех блюд. На это предложение монжно ответить согласием или отказом, а также проигнорировать его. Это **НЕ** приведёт к поломке бота.

> [!WARNING]
> ВАЖНО: при заполнении шаблона следует соблюдать синтаксис. К примеру "Огурец - 1". 

В бота вшита небольшая защита от опечаток, и если вы введёте "Огурец -1", "ОГУРЕЦ - 1", "огурец -1", "огурец - 1" или "ОГУРЕЦ -1", ничего не случится. Также в боте присутсвует простая проверка на ошибки ввода данных. К примеру, при вводе случайного набора символов или "Огурец", вы получите сообщение, что данные неверны, а если вы введёте "Огурец -", то бот сообщит, что ожидает от вас значения 0 или 1, и укажет конкретные ингредиенты, где их необходимо вписать. При этом после сообщения об ошибке достаточно ещё раз отправить исправленное сообщение. Никаких дополнительных действий не требуется.

После завершения процесса ввода данных (или использования сохранённых) бот предложит вам:
- Посчитать красный лист
- Посчитать жёлтый лист
- Посчитать зелёный лист
- Вернуться в главное меню
- Посчиать листы заново

При выборе пересчёта листов всё описанное ранее повторится, но без возможности использовать сохранённые ранее данные. Помимо этого в процессе ввода данных бот предложит Вам вернуться назад, если вы запустили эту функцию случайно.

#### Команда "Помощь":
Команда "Помощь" вызовет краткую инструкцию по работе с ботом, после чего предложит вернуться в начало.

#### Команда "Поиск":
Команда поиск предлагает нам два варианта поиска:
1. По ингредиенту
2. По названию блюда

**По ингредиенту**

Этот вариант осуществляется с помощью отправки сообщения с следующим синтаксисисом: "*ингредиент_1" или "*ингредиент_1, ингредиент_2". В первом случае будут выведены все блюда, содержащие ингредиент_1, а во втором все блюда, содеращие ингредиент_1 **ИЛИ** ингредиент_2. Количество ингредиентов в данной последовательности не ограничено. В случае ввода несуществующего ингредиента, бот сообщит об этом.

**По названию блюда**

Этот вариант предполагает, что вы полностью или частично введёте название блюда. Предположим, у нас есть блюдо "блин_1" и "блин_12". При вводе "блин_12" бот выдаст нам технологическую карту на данное блюдо. Но если мы введём "блин_1", бот оправит нам сообщение с пронумерованным списком "однофамильцев", и попросит нас отправить **ТОЛЬКО** номер конкретного блюда. Если отправить что-то другое, бот сообщит, что в списке нет такого номера, и будет ждать пока вы введёте существующий номер. После ввода нужного номера бот отправит вам технологическую карту на нужное блюдо. Если при этом вводить несуществующие блюда, бот сообщит, что такого блюда нет в базе данных.

Также в начале поиска бот опционаьно предлагает показать список заготовок.

### 2. База данных блюд: 
Данная база данных содержит в себе три основные таблицы: 
- [Блюда](#таблица-блюда)
- [Блюда для бота](#таблица-блюда-для-бота)
- [Список ингредиентов](#таблица-список-ингредиентов)

#### Таблица "Блюда":
```SQLite
CREATE TABLE "dishes" (
	"name_of_dish"	TEXT,
	"ingredients"	TEXT,
	"comments"	TEXT,
	"workpiece"	INTEGER
)
```

**Поле "name_of_dish".**

Для операции поиска и вывода технологической карты бот ориентируется на "класс" блюда. Примеры классов: суп, блин, салат и так далее. Данные классы также указаны в коде бота в функции get_search_request_func(x), в связи с чем при изменении колличесва классов в базе данных необходимо будет изменить их и там.

Учитывая сказанное выше, это поле содержит в себе название блюда и его класс перед ним. К примеру: салат "Цезарь", суп "Солянка", соус сливочный, блин с сёмгой.

**Поле "ingredients".**

В этом поле информация записывается следующим образом: "ингредиент, количество, ингредиент, количество". Важно сохранять разделитель ", ", иначе это приведёт к поломке бота. Количесво ингредиента вводится в граммах (только цифра).

**Поле "comments".**

Это поле содержит в себе пошаговый рецепт.

**Поле "workpiece".**

Это поле содержит в себе значение 0 или 1. 1 - данное блюдо является заготовкой, 0 - не является заготовкой.

#### Таблица "Блюда для бота":
```SQLite
CREATE TABLE "dishes_for_bot" (
	"name_of_dish"	TEXT,
	"ingredients"	TEXT
)
```

Поля этой таблицы абсолютно аналогичны предыдущей. Данная таблица была созда для облегчения написания и тестирования бота, но при необходимости её можно убрать (предварительно переписав зависимости в коде, заменив на таблицу блюд). 

Основное различие между ними: в столбце ингредиенты нет граммовок, так как данная таблица использовалась для создания листов, а не для поиска рецептов и создания технологических карточек. Если возникают какие-либо проблемы с данной таблицей, запустите [пользовательские скрипты](#5.-пользовательские-скрипты) для базы данных, и всё будет исправлено.

#### Таблица "Список ингредиентов":
```SQLite
CREATE TABLE "list_of_ingredients" (
	"ingredient"	TEXT,
)
```

Данное поле принимает в себя название одного ингредиента (заготовки могут быть ингредиентами). Оно используется для шаблона ингредиентов и помогает контролировать, какие ингредиенты существуют.

### 3. База данных пользователей: 
```SQLite
CREATE TABLE "user_data" (
          "user_id" INTEGER PRIMARY KEY,
          "state" INTEGER,
          "switch" INTEGER,
          "yellow_list" TEXT,
          "green_list" TEXT,
          "stop_list" TEXT,
          "list_of_dishes" TEXT,
          "parameters" TEXT,
          "list_of_variants" TEXT,
          "list_of_outputs" TEXT,
          "iteration" INTEGER
)
```

Все поля, кроме "user_id" являются глобальными переменными, так как это поле является id пользователя в телеграмме. Осуществляет работу многопользовательского режима.

### 4. Скрипт перевода в .tex документ: 
Скрипт на основе базы данных блюд создаёт документ с расширением .tex. Это позволяет, используя компилятор LaTeX, перевести базу данных в удобные технологические карты для поваров. Все библиотеки, необходимые для наиболее удачной компиляции, заранее подобраны, и вписаны в итоговый файл. Достаточно открыть полученный документ в LaTeX и запустить компиляцию. Документ отсортирован по категориям блюд (смотри [базы данных блюд](#таблица-блюда)) и по алфавиту построчно.

### 5. Пользовательские скрипты: 
Набор отдельных скриптов, производящих обновление и перезапись базы данных. а также создание и обновление дампа базы данных. При запуске происходит запрос на обновление/создание дампа базы данных (вшита защита от случайного нажатия), после чего происходит пересортировка в алфавитном порядке блюд и заготовок, обновляются списки ингредиентов и списки блюд для бота (смотри [базы данных блюд](#2.-база-данных-блюд)).
