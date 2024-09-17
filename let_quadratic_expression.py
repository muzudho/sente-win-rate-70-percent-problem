#
# 計算
# python let_quadratic_expression.py
#
#   二次式を探すのに使う
#

import traceback
import datetime
import random
import math

from library import CoinToss


SUMMARY_FILE_PATH = 'output/let_quadratic_expression.log'


# 連続コイントス
INPUT_DATA = [
    # p       ... 表が出る確率
    # b_point ... 先手の何本先取制
    # w_point ... 後手の何本先取制
    #
    #  p      b_point  w_point
    #  -----  -------  -------
    [  0.50,       1,        1 ],
    [  0.51,       1,        1 ],
    [  0.52,      25,       23 ],
    [  0.53,      17,       15 ],
    [  0.54,      14,       12 ],
    [  0.55,      11,        9 ],
    [  0.56,      10,        8 ],
    [  0.57,      17,       13 ],
    [  0.58,      15,       11 ],
    [  0.59,       7,        5 ],
    [  0.60,      21,       14 ],
    [  0.61,       6,        4 ],
    [  0.62,       8,        5 ],
    [  0.63,      15,        9 ],
    [  0.64,       5,        3 ],
    [  0.65,       9,        5 ],
    [  0.66,      17,        9 ],
    [  0.67,      14,        7 ],
    [  0.68,       6,        3 ],
    [  0.69,       4,        2 ],
    [  0.70,       2,        1 ],
    [  0.71,       2,        1 ],
    [  0.72,      20,        8 ],
    [  0.73,      13,        5 ],
    [  0.74,       8,        3 ],
    [  0.75,      44,       15 ],
    [  0.76,      12,        4 ],
    [  0.77,       6,        2 ],
    [  0.78,      17,        5 ],
    [  0.79,       3,        1 ],
    [  0.80,      11,        3 ],
    [  0.81,      16,        4 ],
    [  0.82,       8,        2 ],
    [  0.83,      23,        5 ],
    [  0.84,       4,        1 ],
    [  0.85,      10,        2 ],
    [  0.86,      17,        3 ],
    [  0.87,       5,        1 ],
    [  0.88,      20,        3 ],
    [  0.89,       6,        1 ],
    [  0.90,      42,        5 ],
    [  0.91,      27,        3 ],
    [  0.92,      20,        2 ],
    [  0.93,      23,        2 ],
    [  0.94,      11,        1 ],
    [  0.95,      32,        2 ],
    [  0.96,      17,        1 ],
    [  0.97,      23,        1 ],
    [  0.98,      34,        1 ],
    [  0.99,      67,        1 ],
]

#b_point = 3   # NOTE 先手勝率80% なら、黒の４本先取より、黒の３本先取の方が勝率５割に近い


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for input_datum in INPUT_DATA:
            # 先手勝率
            black_win_rate=input_datum[0]

            # 先手の何本先取制
            b_point=input_datum[1]

            # 後手の何本先取制
            w_point=input_datum[2]

            # 比
            target_ration = b_point / w_point
            inverse_target_ration = w_point / b_point

            # 仮説の二次式
            #x = 1 - black_win_rate
            #x = 1 - math.sqrt(black_win_rate)
            #x = 1 - (black_win_rate - 0.5)
            #a = 0
            #quadratic_expression = x**2 + x + a
            #quadratic_expression = x**2 + (0 * x) + a
            #quadratic_expression = x**2 - (x) + (0)

            # これが近い
            quadratic_expression = 1 - (2 * black_win_rate - 1)

            # 誤差
            error = inverse_target_ration - quadratic_expression

            #print(f"[{datetime.datetime.now()}] 先手勝率{black_win_rate:4.2f}  先手{b_point:2}本先取/後手{w_point:2}本先取＝比{target_ration:8.4f}逆{inverse_target_ration:8.4f}  仮説の二次式＝{quadratic_expression:8.4f}  誤差{error:8.4f}")
            print(f"[{datetime.datetime.now()}] 先手勝率{black_win_rate:4.2f}  先手{b_point:2}本先取/後手{w_point:2}本先取＝逆数{inverse_target_ration:8.4f}  仮説の式 1 - (2 * 先手勝率 - 1)＝{quadratic_expression:8.4f}  誤差{error:8.4f}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
