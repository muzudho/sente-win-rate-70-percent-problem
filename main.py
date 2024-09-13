# python main.py
import traceback
import random
import math

# 四捨五入 📖 [Pythonで小数・整数を四捨五入するroundとDecimal.quantize](https://note.nkmk.me/python-round-decimal-quantize/)
from decimal import Decimal, getcontext, ROUND_HALF_UP

# 黒。先手
BLACK = 1

# 白。後手
WHITE = 2


def coin(black_rate):
    """表が黒、裏が白のコイン

    Parameters
    ----------
    black_rate : float
        黒が出る確率。例： 黒が７割出るなら 0.7
    """
    if random.random() < black_rate:
        return BLACK
    return WHITE


def n_bout(n, black_rate, white_require):
    """ｎ本勝負
    
    n はコインを振る回数。全部黒が出たら黒の勝ち、white_require 回白が出れば白の勝ち。

    例えば n=1 なら、コインを最大１回振る。１勝先取で勝ち。
    n=2 なら、コインを最大２回振る。２勝先取で勝ち。白は１勝のアドバンテージが付いている。
    n=3 なら、コインを最大３回振る。３勝先取で勝ち。白は２勝のアドバンテージが付いている。
    以下同様。

    Parameters
    ----------
    n : int
        ｎ本勝負
    black_rate : float
        黒番の勝率。例： 黒番の勝率が７割なら 0.7
    white_require : int
        白が勝つのに必要な番数
    
    Returns
    -------
    winner_color : int
        勝った方の色
    """
    white_count_down = white_require

    for i in range(0, n):
        if coin(black_rate) == WHITE:
            white_count_down -= 1
            if white_count_down < 1:
                return WHITE

    return BLACK


def n_round(black_win_rate, bout_count, white_require, round_count):
    """ｎ回対局

    ｎ回対局して黒が勝った回数を返す。
    
    Parameters
    ----------
    black_win_rate : float
        黒番の勝率。例： 黒番が７割勝つなら 0.7
    bout_count : int
        ｎ本勝負。例： ３本勝負なら 3
    white_require : int
        白が勝つのに必要な番数
    round_count : int
        ｎ回対局
    
    Returns
    -------
    black_win_count : int
        黒の勝った数
    """
    black_win_count = 0

    for i in range(0, round_count):
        if n_bout(bout_count, black_win_rate, white_require) == BLACK:
            black_win_count += 1

    return black_win_count


def round_letro(number):
    """四捨五入

    📖 [Pythonで小数・整数を四捨五入するroundとDecimal.quantize](https://note.nkmk.me/python-round-decimal-quantize/)

    Parameters
    ----------
    number : float
        四捨五入したい数
    
    Returns
    -------
    answer : int
        整数
    """
    return int(Decimal(str(number)).quantize(Decimal('0'), ROUND_HALF_UP))


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        round_count = 2_000_000

        # 0.50 ～ 0.99 まで試算
        rule_list = [
            # black_win_rate, bout_count, white_require
            # -----------------------------------------
            # round_letro(1/(1-black_win_rate)-1)
            [0.50,  1,  1], # 0.5:0.5
            [0.51,  1,  1],
            [0.52,  1,  1],
            [0.53,  1,  1],
            [0.54,  1,  1],
            [0.55,  1,  1],
            [0.56,  1,  1],
            [0.57,  1,  1],
            [0.58,  1,  1],
            [0.59,  1,  1],

            # 60％で既存式では 2-bout になるが、調整黒番勝率が 35.9915 ％ に下がってしまう。調整を入れる
            [0.60,  2+2,  1+2], # 1:1=60.0%, 2:1=35.9%, 3:2=64.8%, 4:3=
            [0.61,  2+2,  1+2],
            [0.62,  2+2,  1+2],
            [0.63,  2+2,  1+2],
            [0.64,  2+2,  1+2],
            [0.65,  2+2,  1+2],
            # 0.65 まで調整

            [0.66,  2,  1],
            [0.67,  2,  1],
            [0.68,  2,  1],
            [0.69,  2,  1],
            [0.70,  2,  1],
            [0.71,  2,  1],
            [0.72,  3,  2],
            [0.73,  3,  2],
            [0.74,  3,  2],
            [0.75,  3,  2],
            [0.76,  3,  2],
            [0.77,  3,  2],
            [0.78,  4,  3],
            [0.79,  4,  3],
            [0.80,  4,  3],
            [0.81,  4,  3],
            [0.82,  5,  4],
            [0.83,  5,  4],
            [0.84,  5,  4],
            [0.85,  6,  5],
            [0.86,  6,  5],
            [0.87,  7,  6],
            [0.88,  7,  6],
            [0.89,  8,  7],
            [0.90,  9,  8],
            [0.91, 10,  9],
            [0.92, 12, 11],
            [0.93, 13, 12],
            [0.94, 16, 15],
            [0.95, 19, 18],
            [0.96, 24, 23],
            [0.97, 32, 31],
            [0.98, 49, 48],
            [0.99, 99, 98],
        ]

        for rule in rule_list:
            black_win_rate=rule[0]
            bout_count=rule[1]
            white_require=rule[2]

            # （仮説）何本勝負にするかは、以下の式で求まる
            # bout_count = round_letro(1/(1-black_win_rate)-1)
            # print(f"試算： 1 / ( 1 - {black_win_rate} ) - 1 = {bout_count} ※小数点以下四捨五入")
            # bout_count = math.floor(1/(1-black_win_rate)-1)
            # print(f"試算： 1 / ( 1 - {black_win_rate} ) - 1 = {bout_count} ※小数点以下切り捨て")
            #bout_count = math.ceil(1/(1-black_win_rate)-1)
            #print(f"試算： 1 / ( 1 - {black_win_rate} ) - 1 = {bout_count} ※小数点以下切り上げ")

            black_win_count = n_round(
                black_win_rate=black_win_rate,
                bout_count=bout_count,
                white_require=white_require,
                round_count=round_count)

            with open('result_summary.log', 'a', encoding='utf8') as f:
                text = f"先手勝率：{black_win_rate:4.02f}  {bout_count:2}本勝負×{round_count}回  調整先手勝率：{black_win_count * 100 / round_count:7.04f} ％\n"

                f.write(text)
                print(text, end='')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
