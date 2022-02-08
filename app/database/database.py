import mysql.connector

from settings import DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_TABLE_NAME


def connect_database():
    try:
        conn = mysql.connector.connect(host=DATABASE_HOST, database=DATABASE_NAME, user=DATABASE_USER,
                                       password=DATABASE_PASSWORD)
        return conn
    except BaseException as error:
        raise ValueError(f'Ocorreu um erro salvar os registros no banco de dados, erro {error}')


def insert(regs: dict) -> object:
    conn = connect_database()
    cursor = conn.cursor()

    for reg in regs:

        if not isinstance(reg, list):
            mms_field = reg['mms_days']
            sql_insert = f'insert into {DATABASE_NAME}.{DATABASE_TABLE_NAME} (pair, timestamp, mms_{mms_field}) values (%s, %s, %s)'
            cursor.execute(sql_insert, (reg['pair'], reg['timestamp'], reg['mms']))
        else:
            for item in reg:
                mms_field = item['mms_days']
                sql_insert = f'insert into {DATABASE_NAME}.{DATABASE_TABLE_NAME} (pair, timestamp, mms_{mms_field}) values (%s, %s, %s)'
                cursor.execute(sql_insert, (item['pair'], item['timestamp'], item['mms']))

    conn.commit()
    conn.close()


def select_regs(pair: str, timestamp_ini: int, timestamp_fim: int, range_days: int, ingnore_zero_values=True) -> dict:
    conn = connect_database()

    cursor = conn.cursor()

    pair = '"' + pair + '"'
    field = f'mms_{range_days}'

    sql_filter = ''
    if ingnore_zero_values:
        sql_filter = f'and {field} <> 0 '

    _sql = f'select timestamp, {field} ' \
           f'from {DATABASE_NAME}.{DATABASE_TABLE_NAME} ' \
           f'where pair = {pair} ' \
           f'and timestamp >= {timestamp_ini} ' \
           f'and timestamp <= {timestamp_fim} ' \
           f'{sql_filter} ' \
           f'order by timestamp'

    cursor.execute(_sql)

    response = cursor.fetchall()

    ret_list = []
    for res in response:
        payload = {'timestamp': res[0], 'mms': res[1]}
        ret_list.append(payload)

    return ret_list
