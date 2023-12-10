import sqlite3 as sq


def get_num(string, array):
    counter = 0
    for h in range(len(array)):
        if string in array[h]:
            counter += 1

    return counter


def table_func(a):
    global names
    global ingredients
    global comments
    t = f"""\\begin{{tabular}}{{|p{{0.25cm}}|p{{5.75cm}}|p{{2cm}}|}}
\\multicolumn{{3}}{{p{{8cm}}}}{{\\textbf{{{names[a]}}}}}\\\\
\\hline
\\textbf{{\\small{{№}}}} & \\textbf{{\\small{{Ингредиенты}}}} & \\textbf{{\\small{{Гр./Шт.}}}}\\\\
"""

    for j in range(len(ingredients[a])):
        if j % 2 == 0:
            t += f"""\\hline
{(j // 2) + 1} & {ingredients[a][j]} & {ingredients[a][j + 1]} \\\\"""
            print(f"[{a}][{j}]")

    t += f"""\\hline
\\multicolumn{{3}}{{p{{8cm}}}}{{\\vspace{{1pt}}\\textbf{{Комментарий:}}\\par\\small{{{comments[a]}}}}}\\\\
\\end{{tabular}}"""

    return t


with sq.connect('recipes.db') as conn:
    cur = conn.cursor()
    cur.execute(f'SELECT name_of_dish, ingredients, comments FROM dishes')
    result = cur.fetchall()

for i in range(len(result)):
    result[i] = list(result[i])

begining = """
\\documentclass[a4paper, 10pt, oneside]{book}

\\usepackage[english,russian]{babel}
\\usepackage{geometry}
\\usepackage{float}

\\geometry{a4paper, rmargin=12.7mm, lmargin=12.7mm, bmargin=12.7mm, tmargin=12.7mm}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\\begin{document}
\\pagestyle{plain}

"""

ending = """
\\end{document}"""

for i in result:
    i[1] = i[1].split(', ')

result.sort()

text = ''
text += begining

names = []
for i in range(len(result)):
    names.append(result[i][0])
    names[i] = names[i].replace('"', "''")

ingredients = []
for i in range(len(result)):
    ingredients.append(result[i][1])

comments = []
for i in range(len(result)):
    comments.append(result[i][2])

dish_type = ["Блины", "Заготовки", "Каши", "Крем-супы", "Омлеты", "Салаты", "Соусы", "Тесто", "Вафли"]
dish_type.sort()
shadow_dish_type = ["Блин", "Заготовка", "Каша", "Крем-суп", "Омлет", "Салат", "Соус", "Тесто", "Вафля"]
shadow_dish_type.sort()

total = 0
for k in range(len(dish_type)):
    text += f'''
\\newpage
\\begin{{center}}
\\textbf{{\\Large{{{dish_type[k]}}}}}
\\end{{center}}


'''
    c = get_num(shadow_dish_type[k], names)
    for i in range(len(names)):
        if shadow_dish_type[k] in names[i]:
            if i % 2 == 0:
                if i <= (c - 2):
                    text += f"""\\begin{{table}}[H]
\\begin{{minipage}}{{0.45\\textwidth}}
{table_func(i)}
\\end{{minipage}}
\\hfill
\\begin{{minipage}}{{0.45\\textwidth}}
{table_func(i + 1)}
\\end{{minipage}}
\\end{{table}}

"""
                if i == (c - 1):
                    text += f"""\\begin{{table}}[H]
\\begin{{minipage}}{{0.45\\textwidth}}
{table_func(i)}
\\end{{minipage}}
\\end{{table}}

"""

    names = names[c:].copy()
    ingredients = ingredients[c:].copy()
    comments = comments[c:].copy()
    print('------------------------------')
    print(c)
    print('------------------------------')
    total += c

print('end')
print(f"total {total}")
text += ending

with open('calc.tex', 'w', encoding='utf-8') as f:
    f.write(text)
