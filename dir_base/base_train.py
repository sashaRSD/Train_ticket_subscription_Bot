import sqlite3 as sq
from datetime import datetime


def sql_start():
    global base, cur
    base = sq.connect('dir_base/base_train.db')
    cur = base.cursor()
    if base:
        print('Data base connect OK!')
    base.execute('CREATE TABLE IF NOT EXISTS data(train TEXT PRIMARY KEY,'
                 'sitting INT, '
                 'platzkarte_low INT, platzkarte_up INT,'
                 'compartment_low INT, compartment_up INT,'
                 'suite_low INT, suite_up INT,'
                 'soft INT,'
                 'time_departure DATETIME)')
    base.commit()


async def sql_add_train(train_number, time_departure):
    cur.execute('INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (train_number, 0, 0, 0, 0, 0, 0, 0, 0, time_departure))
    base.commit()


async def sql_read_train(train_number):
    return cur.execute('SELECT * FROM data WHERE train == ?', (train_number,)).fetchall()


async def sql_read_time_train(train_number):
    return cur.execute('SELECT `time_departure` FROM data WHERE train == ?', (train_number,)).fetchall()


async def sql_read_all_train():
    return cur.execute('SELECT * FROM data').fetchall()


async def sql_update_train(train_number, all_seats):
    cur.execute('UPDATE  data SET sitting = ?,'
                ' platzkarte_low = ?, platzkarte_up = ?,'
                ' compartment_low = ?, compartment_up = ?,'
                ' suite_low = ?, suite_up = ?,'
                ' soft = ?'
                ' WHERE train == ?', (all_seats[0], all_seats[1], all_seats[2], all_seats[3],
                                                 all_seats[4], all_seats[5], all_seats[6], all_seats[7], train_number))
    base.commit()


async def sql_delete_train(train_number):
    cur.execute('DELETE FROM data WHERE train == ?', (train_number,))
    base.commit()


async def sql_delete_all():
    cur.execute('DELETE FROM data')
    base.commit()


async def sql_delete_old():
    table = cur.execute('SELECT * FROM data').fetchall()
    for i_table in table:
        if datetime.strptime(i_table[-1], "%Y-%m-%d %H:%M:%S") < datetime.now():
            cur.execute('DELETE FROM data WHERE train == ?', (i_table[0],))
            base.commit()


