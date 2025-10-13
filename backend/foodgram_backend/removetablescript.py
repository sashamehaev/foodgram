import sqlite3

# Создаем подключение к базе данных (файл my_database.db будет создан)
connection = sqlite3.connect('db.sqlite3')

cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
DROP TABLE django_migrations;
''')

connection.close()