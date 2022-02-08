import json
from datetime import datetime, timedelta

import requests

from database.database import select_regs, insert
from settings import DEBUG, DEFAULT_RANGE


def __get_close_by_day(candles: dict, search_day: int):
    for reg in candles:
        if reg['day_number'] == search_day:
            return reg['close']


def get_calculed_mms(candles: dict):
    mms_days_to_calc = [20, 50, 200]
    calculated = []

    for mms_days in mms_days_to_calc:

        idx = 1
        for candle in candles:
            if idx >= mms_days:
                sum_value = 0
                i = mms_days
                idx_aux = idx
                while i > 0:
                    sum_value = sum_value + __get_close_by_day(candles, idx_aux)
                    i -= 1
                    idx_aux -= 1
                mms = sum_value / mms_days
                payload = {'timestamp': candle['timestamp'], 'close': candle['close'], 'mms': mms,
                           'pair': candle['pair'], 'mms_days': mms_days}
                calculated.append(payload)
            else:
                mms = 0
                payload = {'timestamp': candle['timestamp'], 'close': candle['close'], 'mms': mms,
                           'pair': candle['pair'], 'mms_days': mms_days}
                calculated.append(payload)

            idx += 1

    return calculated


def insert_into_database(mms_list: dict):
    try:
        insert(mms_list)
    except BaseException as error:
        print(f'Ocorreu um erro salvar os registros no banco de dados, erro {error}')
        raise


def get_candle_calc_mms_store_database(from_timestamp: int, to_timestamp: int, pair: str):
    try:
        candles = get_candle_list(from_timestamp, to_timestamp, pair)

        calculated_mms = get_calculed_mms(candles)

        insert_into_database(calculated_mms)
    except BaseException as error:
        print(error)
        raise


def get_candle_list(from_timestamp: int, to_timestamp: int, pair: str):
    candles = []

    if DEBUG:
        with open(f'EXAMPLE_{pair}.json') as file:
            values = json.load(file)
    else:
        values = requests.get(
            f'https://mobile.mercadobitcoin.com.br/v4/BRL{pair}/candle?from={from_timestamp}to={to_timestamp}&precision=1d')

        if values.status_code != 200:
            raise BaseException('API Indisponível')

    list_candles = values['candles']

    idx = 1
    for candles_reg in list_candles:
        payload = {'pair': pair, 'timestamp': candles_reg['timestamp'], 'close': candles_reg['close'],
                   'day_number': idx}
        candles.append(payload)
        idx += 1

    return candles


def return_mms_calculed_database(pair: str, from_timestamp: int, to_timestamp: int, range_days: int) -> dict:
    return select_regs(pair, from_timestamp, to_timestamp, range_days)


def check_not_calculed_days_database(pair: str, from_timestamp: int, to_timestamp: int) -> dict:

    list_days_not_found = []
    day_count = abs((datetime.fromtimestamp(from_timestamp) - datetime.fromtimestamp(to_timestamp)).days)

    for i in range(day_count):
        timestamp_to_find = int(datetime.timestamp(datetime.fromtimestamp(from_timestamp) + timedelta(i)))
        reg = select_regs(pair, timestamp_to_find, timestamp_to_find, DEFAULT_RANGE, False)
        if not reg:
            list_days_not_found.append({'timestamp': timestamp_to_find})

    return list_days_not_found

