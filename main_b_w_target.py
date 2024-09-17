#
# 計算
# python main_b_w_target.py
#
#   先手先取本数、後手先取本数を求める
#

import traceback
import datetime
import random
import math

from library import black_win_rate_to_b_w_targets


SUMMARY_FILE_PATH = 'main_b_w_target.log'

# 下の式になるような、先手先取本数、後手先取本数を求めたい。
#
#
# 　　　　   先手先取本数
# ───────────────────────────────　＝　先手勝率
# 　先手先取本数　＋　後手先取本数
#
# ここで、先手先取本数、後手先取本数は１以上の整数とし、先手先取本数　≧　後手先取本数。
#
#
# 例：
#
# 　　　７
# ─────────────　＝　０．７
# 　７　＋　３
#
#
# このような数式はすぐに作れる。例えば　先手勝率０．６５なら、
#
# 　　　 ６５
# ─────────────────　＝　０．６５
# 　６５　＋　３５

# 0.50 ～ 0.99 まで試算
INPUT_DATA = [
    [0.50],
    [0.51],
    [0.52],
    [0.53],
    [0.54],
    [0.55],
    [0.56],
    [0.57],
    [0.58],
    [0.59],
    [0.60],
    [0.61],
    [0.62],
    [0.63],
    [0.64],
    [0.65],
    [0.66],
    [0.67],
    [0.68],
    [0.69],
    [0.70],
    [0.71],
    [0.72],
    [0.73],
    [0.74],
    [0.75],
    [0.76],
    [0.77],
    [0.78],
    [0.79],
    [0.80],
    [0.81],
    [0.82],
    [0.83],
    [0.84],
    [0.85],
    [0.86],
    [0.87],
    [0.88],
    [0.89],
    [0.90],
    [0.91],
    [0.92],
    [0.93],
    [0.94],
    [0.95],
    [0.96],
    [0.97],
    [0.98],
    [0.99],
]


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for input_datum in INPUT_DATA:
            # 先手勝率
            black_win_rate=input_datum[0]

            b_point, w_point = black_win_rate_to_b_w_targets(p=black_win_rate)


            with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = f"[{datetime.datetime.now()}]  先手勝率：{black_win_rate:4.2f}  先取本数　黒：白＝{b_point:>2}：{w_point:>2}"
                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
