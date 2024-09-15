# 理論値の出力
#
#   python main_theoretical_value.py
#

import traceback
from library import round_letro, white_win_rate, white_win_value, black_win_value



########################################
# コマンドから実行時
########################################

# 0.50 ～ 0.99 まで試算
rule_list = [
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

if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        for rule in rule_list:
            # 初期値
            black_win_rate=rule[0]

            # 後手勝率
            w_win_rate = white_win_rate(black_win_rate=black_win_rate)

            # 先手の勝ちの価値
            b_win_value = black_win_value(white_win_rate=w_win_rate)

            # 後手の勝ちの価値
            w_win_value = white_win_value(black_win_rate=black_win_rate)

            print(f"先手勝率{black_win_rate:4.2f}  先手の勝ちの価値{b_win_value:6.4f}  後手の勝ちの価値{w_win_value:7.4f}  四捨五入{round_letro(w_win_value):2}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
