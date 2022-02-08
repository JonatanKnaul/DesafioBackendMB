from datetime import datetime, timedelta

from flask import Flask, request, jsonify

from services.mms import return_mms_calculed_database, get_candle_calc_mms_store_database, \
    check_not_calculed_days_database
from settings import DEBUG, FROM_DEFAULT_TIMESTAMP, TO_DEFAULT_TIMESTAMP, DEFAULT_COIN

app = Flask(__name__)


@app.route('/')
def test():  # put application's code here
    return 'This API is On!'


@app.route('/check_regs', methods=['GET'])
def check_calculated_regs_on_database():
    try:
        return jsonify(check_not_calculed_days_database(DEFAULT_COIN, FROM_DEFAULT_TIMESTAMP, TO_DEFAULT_TIMESTAMP)), 200
    except BaseException as error:
        return jsonify(f'{error}'), 500


@app.route('/calc_mms', methods=['GET'])
def calc_mms():
    coin_list = ['BTC', 'ETH']
    if not DEBUG:
        from_timestamp = datetime.timestamp(datetime.today())
        to_timestamp = datetime.timestamp(datetime.today() - timedelta(days=-365))
    else:
        from_timestamp = FROM_DEFAULT_TIMESTAMP
        to_timestamp = TO_DEFAULT_TIMESTAMP

    list_processed_coin = []
    for coin in coin_list:
        try:
            get_candle_calc_mms_store_database(from_timestamp, to_timestamp, coin)
            list_processed_coin.append(f'{coin} processada com sucesso!')
        except BaseException as error:
            list_processed_coin.append(f'{coin} processada com erro: {error}')

    return jsonify(list_processed_coin), 200


@app.route('/<pair>/mms', methods=['GET'])
def return_mms(pair):
    try:
        from_timestamp = request.args.get('from', type=int)
        to_timestamp = request.args.get('to', type=int)
        range_days = request.args.get('range', type=int)

        data_ini = datetime.fromtimestamp(from_timestamp)
        data_fim = datetime.fromtimestamp(to_timestamp)

        qtd_dias = abs((data_ini - data_fim).days)

        if qtd_dias > 365:
            raise 'O periodo escolhido não pode ser maior que 1 ano.'

        return jsonify(return_mms_calculed_database(pair, from_timestamp, to_timestamp, range_days)), 200

    except BaseException as error:
        return jsonify(f'{error}'), 500


if __name__ == '__main__':
    app.debug = True
