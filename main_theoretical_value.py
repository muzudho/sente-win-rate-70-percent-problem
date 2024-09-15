# 理論値の出力
#
#   python main_theoretical_value.py
#

import traceback
import math
from library import round_letro, count_of_decimal_places, white_win_rate, white_win_value, black_win_value



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
            # ------

            # 先手勝率
            black_win_rate=rule[0]
            # 小数部の桁数
            d = count_of_decimal_places(black_win_rate)
            print(f"先手勝率{black_win_rate:4.2f}  小数部の桁数{d}  ", end='')

            # 計算過程
            # --------

            # 後手勝率
            w_win_rate = white_win_rate(black_win_rate=black_win_rate)
            #print(f"後手勝率{w_win_rate:4.2f}  ", end='')

            # 先手勝率と後手勝率を整数にする
            d_b_win_rate = round_letro((10**d) * black_win_rate)    # NOTE 4 が 内部的に 3.9999... だったりするので、四捨五入している
            print(f"先後勝率整数比　{d_b_win_rate:2}：", end='')
            d_w_win_rate = round_letro((10**d) * w_win_rate)        # NOTE 4 が 内部的に 3.9999... だったりするので、四捨五入している
            print(f"{d_w_win_rate:2}  ", end='')

            # 先手の勝ちの価値
            # b_win_value = black_win_value(white_win_rate=w_win_rate)
            # print(f"先手の勝ちの価値{b_win_value:7.4f}  ", end='')

            # 後手の勝ちの価値
            w_win_value = white_win_value(black_win_rate=black_win_rate)

            # 先手のｎ本先取制
            b_win_required = math.floor(w_win_value)

            # 黒/白の商の整数部
            quotient = round_letro(d_b_win_rate / d_w_win_rate)     # NOTE 4 が 内部的に 3.9999... だったりするので、四捨五入している

            # 商の整数部
            print(f"先手の{quotient:2}本先取制  ", end='')

            # 剰余
            remainder = d_b_win_rate % d_w_win_rate
            
            print(f"余り{remainder:2}  ", end='')

            # 余り解消の周期
            if remainder == 0:
                print() # 改行

            else:
                cycle = d_b_win_rate / remainder
                print(f"余り解消の周期{cycle:7.4f}  ", end='')

                # 閏対局を１つ求める
                leap_game_1 = math.floor(cycle)
                remainder_1 = d_b_win_rate - (leap_game_1 * remainder)

                #print(f"先手勝率{black_win_rate:4.2f}　後手勝率{w_win_rate:4.2f}  ", end='')
                #print(f"後手の勝ちの価値{w_win_value:7.4f}  先手の{b_win_required:2}本先取制  ", end='')
                print(f"閏対局[{leap_game_1:2} 余{remainder_1:2}]")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
