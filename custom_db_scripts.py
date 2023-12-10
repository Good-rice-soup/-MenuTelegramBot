import sqlite3 as sq


def update_ingredients():
    with sq.connect('recipes.db') as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT ingredients FROM dishes')
        result = cur.fetchall()

        a = []
        for i in result:
            a.append(list(i)[0].split(', '))

        b = []
        for i in a:
            for j in i:
                if (j not in b) and (not j.isdigit()):
                    b.append(j)
        b.sort()

        cur.execute(f'DELETE FROM list_of_ingredients')
        for i in b:
            cur.execute(f'INSERT INTO list_of_ingredients(ingredient) VALUES ("{i}")')


def update_dishes_for_bot():
    with sq.connect('recipes.db') as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT name_of_dish, ingredients, workpiece FROM dishes')
        result = cur.fetchall()

        a = []
        for i in result:
            a.append(list(i))

        for i in range(len(a)):
            a[i][1] = a[i][1].split(', ')
            b = []
            for j in a[i][1]:
                if not j.isdigit():
                    b.append(j)
            a[i][1] = ', '.join(b.copy())

        cur.execute(f'DELETE FROM dishes_for_bot')
        for i in a:
            if i[2] == 0:
                cur.execute(f"INSERT INTO dishes_for_bot(name_of_dish, ingredients) VALUES ('{i[0]}', '{i[1]}')")


def make_bd_dump():
    print('Do you want to update your main dump of data base?')
    print('Y\\N')
    x = input()
    if x == 'Y' or x == "y":
        con = sq.connect('recipes.db')
        with open('sql_dump.txt', 'w') as f:
            for line in con.iterdump():
                f.write('%s\n' % line)
            print('All done.')
    elif x == 'N' or x == "n":
        return
    else:
        print("Unknown character.\n")
        make_bd_dump()


def resort_main_table():
    with sq.connect('recipes.db') as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM dishes')
        result = cur.fetchall()
        result.sort()

        cur.execute(f'DELETE FROM dishes')
        for i in result:
            cur.execute(
                f"INSERT INTO dishes(name_of_dish, ingredients, comments, workpiece) VALUES (?, ?, ?, ?)", i)


make_bd_dump()
resort_main_table()
update_ingredients()
update_dishes_for_bot()
