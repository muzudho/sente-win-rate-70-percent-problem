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
            print(f"先手勝率{black_win_rate:4.2f}  ", end='')

            # 小数部の桁数
            d = count_of_decimal_places(black_win_rate)
            #print(f"小数部の桁数{d}  ", end="")

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
            
            print(f"先手余り{remainder:2}  ", end='')

            #print(f"先手勝率{black_win_rate:4.2f}　後手勝率{w_win_rate:4.2f}  ", end='')
            #print(f"後手の勝ちの価値{w_win_value:7.4f}  先手の{b_win_required:2}本先取制  ", end='')

            # 以下で行っているのは、余りの解消
            # -----------------------------
            #
            #   NOTE 余りを全て解消しても、また最初から繰り返しを行うこと
            #

            # 繰り上がり先手勝率点
            carried = remainder

            # 繰り上がり先手勝率点込みの先手勝率点
            hangover_b_win_point = d_b_win_rate + carried

            # 繰り上がりがある場合
            if carried != 0:
                # 次の閏対局
                next_leap = 0

                print(f"余り解消の周期{hangover_b_win_point / quotient:7.4f}  ", end='')

                # 余り解消の周期
                countdown = 10
                while carried != 0 and 0 < countdown:

                    # ※繰り返し

                    # あと何対局すると、余りが後手先取必要本数を上回るか（次の閏対局までの長さ）
                    fill_bouts = math.ceil(d_w_win_rate / carried)
                    print() # 改行
                    print(f"  一対局毎に余りが{carried}ずつ溜まり、{d_w_win_rate}以上になるのが、次の閏対局までの長さ{fill_bouts:2}")

                    if carried != 0:
                        for i in range(0, 1):

                            # 次に余りを解消できる閏対局
                            next_leap += fill_bouts
                            print(f"  次に余りを解消できる閏対局第{next_leap:2}")

                            # 次の繰り上がり先手勝率点
                            carried = d_b_win_rate % carried
                            print(f"  次の繰り上がり先手勝率点{carried}")

                            if carried == 0:
                                print(f"  余りなし")
                                break

                            # 持ち越し勝率点
                            hangover_b_win_point = d_b_win_rate + carried
                            print(f"  持ち越し勝率点{hangover_b_win_point}")

                    countdown -= 1

            print() # 改行


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
