# -MenuTelegramBot

Contents:

[ENG](https://github.com/miss-riss/-MenuTelegramBot/edit/main/README.md#overview)

[RU](https://github.com/miss-riss/-MenuTelegramBot/edit/main/README.md#Общие)

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


## Общие данные:

Этот чат-бот создан для облегчения работы повара.

!!! Работа с ботом: После запуска бота у пользователя появляется три команды:

1)Посчитать листы

2)Вызвать помощь

3)Выполнить поиск по базе данных

При просчитывании листов, если у бота сохранились ранее введённые данные, он преложит использовать их и пропустить процецуру ввода новых. Если выбрать этот вариант, бот сразу предложит перейти к созданию зелёных, жёлтых и красных листов. В противном случае бот предложит отправит сообщение с правилами заполнения (0 -ингредиента нет; 1 - ингредиент есть) и прделожение прислать шаблон, содержащий все ингредиенты изо всех блюд. Можно как ответить на предложение бота согласием или отказом, так и проигнорировать его. Это НЕ приведёт к поломке бота.

ВАЖНО: при заполнении шаблона следует соблюдать синтаксис "Огурец - 1". В бот вшита небольшая защита от опечаток, и если вы введёте "Огурец -1", "ОГУРЕЦ - 1" или "ОГУРЕЦ -1", ничего страшного не произойдёт, однако автор настоятельно не советует вам так поступать. Также в боте присутсвует небольшая проверка на ошибки ввода данных: если вы введёте случайный набор символов или "Огурец", вы получите сообщение, что данные неверны, а если вы введёте "Огурец -", то бот сообщит, что ожидает от вас значения 0 или 1, и укажет конкретные ингредиенты, где необходимо вписать их. При этом после сообщения об ошибке не нужно выходить в меню и начинать ввод ингредиентов заново. Достаточно ещё раз отправить исправленное сообщение.

После этого у вас появится посчитать следующие листы: 1)Красный лист (стоп лист) содержит все блюда, в которых не хватает хотя бы одного ингредиента, что не даёт приготовить данное блюдо. 2)Зелёный лист (доступный к приготовлению лист) содержит все блюда, ингредиенты для которых точно есть. 3)Жёлтый лист (лист ожидания) содержит все остальные блюда, о которых недостаточно информации, чтобы отнести блюдо к красному или жёлтому листу. Также бот предложит Вам вернуться в главное меню и посчиать листы заново. При выборе пересчёта листов всё описанное ранее повторится, но без возможности исполльзовать ранее введённые данные. Помимо этого в процессе ввода данных бот предложит Вам вернуться назад, если вы запустили эту функцию случайно.

Команда "Помощь" вызовет краткую инструкцию по работе с ботом, после чего предложит вернуться в начало.

Команда поиск предлагает нам два варианта поиска:

1)По ингредиенту

2)По названию блюда

Первый вариант осуществляется с помощью отправки сообщения с следующим синтаксисисом: "*ингредиент_1" или "*ингредиент_1, ингредиент_2". В первом случае будут выведены все блюда, содержащие ингредиент_1, а во втором все блюда, содеращие ингредиент_1 ИЛИ ингредиент_2. Соответсвенно, количество ингредиентов в данной последовательности не ограничено. В случае ввода неправильного ингредиента, бот сообщит об этом.

Второй вариант предполагает, что Вы полностью или частично введёте название блюда. Предположим, у нас есть блюдо "блин 1" и "блин 12". Если мы введём "блин 1", бот оправит нам сообщение с пронумерованным списком "однофамильцев", и попросит нас ввести ТОЛЬКО номер конкретного блюда. Если ввести буквенный символ, бот скажет, что он просил цифру, а если ввести неверный номер, он скажет, что тут нет такого номера. При этом бот ранее предложитвернуться в главное меню и будет ждать пока вы не введёте правильный номер. После ввода нужного номера бот отправит нам тех карту на нужный блин. Если при этом вводить несуществующие блюда, бот сообщит, что такого блюда нет в базе данных.

Также в начале поиска бот опционаьно предлагает показать список заготовок.

!!! База данных блюд: Данная база данных содержит в себе три основные таблицы: блюда, блюда для бота, список ингредиентов.

В таблице блюда есть следующие поля: 1)Название блюда 2)Ингредиенты 3)Комментарии 4)Заготовка

Поле "Название блюда" принимает в себя строку. Так как алгоритм поиска в боте и алгоритм создание технической карты для поваров подразумевает ориентирование на "класс" блюда, то необходимо указывать перед названием данную информацию. К примеру: суп "солянка", каша овяная, блин с лососем и так далее. Соответсвующие классы указаны в коде бота в функции get_search_request_func(x), в связи с чем при изменении колличесва классов в базе данных необходимо будет изменить их и там.

Поле "Ингредиенты" принимает в себя строку. Информация записывается следующим образом: "ингредиент, количество, ингредиент, количество". Важно сохранять разделитель ", ", иначе это приведёт к поломке бота. Количесво вводится в граммах (только цифра), иногда в штуках (по контексту)

Поле "Комментарии" содержит в себе строку с пояснениями в приготовлении.

Поле "Заготовка" содержит в себе значение 0 или 1. 1 - данное блюдо является заготовкой, 0 - противоположное 1.

В таблице блюда для бота есть следующие поля: 1)Название блюда 2)Ингредиенты

Правила для этой таблицы абсолютно аналогичны предыдущей. Данная таблица была созда для облегчения написания и тестирования бота, но при необходимости её можно убрать (предварительно переписав данный элемент в коде), заменив на таблицу блюд. основное различие: в столбце ингредиенты нет граммовок, так как данная таблица использовалась для создания красных, жёлтых и зелёных листов, а не для поиска рецептов и создания технических карточек. Если возникают какие-либо проблемы с данной таблицей, запустите кастомные скрипты для базы данных, и всё будет исправлено.

В таблице список инредиентов есть следующие поля: 1)Ингредиент.

Данное поле принимает в себя название одного ингредиента (заготовки могут быть ингредиентами).

!!! База данных пользователей: Данная база данных включает в себя следующие поля: "user_id" INTEGER, "state" INTEGER, "switch" INTEGER, "yellow_list" TEXT, "green_list" TEXT, "stop_list" TEXT, "list_of_dishes" TEXT, "parameters" TEXT, "list_of_variants" TEXT, "list_of_outputs" TEXT, "iteration" INTEGER. Все поля, кроме user_id являются глобальными переменными, так как это поле является id пользователя в телеграмме.

!!! Скрипт перевода в .tex документ: Скрипт на основе базы данных блюд создаёт документ с расширением .tex, что позволяет без проблем с использованием компилятора LaTeX перевести базу данных в удобные технологические карты для поваров. Все необходимые библиотеки для наиболее удачной компиляции заранее подобраны и вписаны в итоговый файл, в связи с чем достаточно лишь открыть полученный документ в LaTeX и запустить компиляцию. Документ отсортирован по категориям блюд (смотри базы данных блюд) и по алфавиту построчно.

!!! Кастомные скрипты: При запуске документа происходит запрос на обновление/создание дампа базы данных (вшита защита от дураков), после чего пересортировываются в алфавитном порядке блюда и заготовки, обновляются списки ингредиентов и списки блюд для бота (смотри базы данных блюд).
