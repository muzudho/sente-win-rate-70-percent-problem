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
            # 説明１　コインの表裏の確率
            # ------------------------

            # 先手勝率
            black_win_rate=rule[0]
            print(f"先手勝率{black_win_rate:4.2f}  ", end='')

            # 後手勝率
            w_win_rate = white_win_rate(black_win_rate=black_win_rate)
            #print(f"後手勝率{w_win_rate:4.2f}  ", end='')


            # 説明２  コインの表裏の確率の整数化
            # --------------------------------

            # 小数部の桁数
            dp_len = count_of_decimal_places(black_win_rate)
            #print(f"小数部の桁数{dp_len}  ", end="")

            scale = 10**dp_len

            # 先手勝率と後手勝率を整数にする
            #
            #   NOTE ここでは、小数点以下切り捨てにするところだが、 4 が 内部的に 3.9999... だったりするので、四捨五入に変更している
            #
            b_point = round_letro(scale * black_win_rate)
            print(f"先後勝率整数比　{b_point:2}：", end='')
            w_point = round_letro(scale * w_win_rate)
            print(f"{w_point:2}  ", end='')


            # 説明３　表のｎ本先取
            # -------------------

            # 黒/白の商の整数部（quotient）
            b_target = math.floor(b_point / w_point)
            print(f"先手の{b_target:2}本先取制  ", end='')

            # # NOTE この計算式では、エラーが出てしまう。 0.5 が 0.050000000000000044 になってる
            # black_target_2 = math.floor(black_win_rate / w_win_rate)
            # if b_target != black_target_2:
            #     raise ValueError(f"{b_target=}  {black_target_2=}  {black_win_rate=}/{w_win_rate=}")


            # 説明４　表がまだ多めに出る得
            # --------------------------

            # 剰余（remainder）。繰り上がり先手勝率点
            carried = b_point % w_point            
            print(f"先手得{carried:2}  ", end='')


            # 以下で行っているのは、余りの解消
            # -----------------------------
            #
            #   方法としては、足し算の筆算の繰り上がりと同じ。
            #   NOTE 余りを全て解消しても、また最初から繰り返しを行うこと
            #


            # 説明５　繰り上がり込みの表のポイント
            # ---------------------------------

            # 繰り上がり先手勝率点込みの先手勝率点
            carryover_b_point = b_point + carried


            # 繰り上がりがある場合
            if carried != 0:
                # 次の閏対局
                next_leap = 0

                print(f"先手得をチャラにするのに必要な次の閏対局", end='')

                # 余り解消の周期
                #
                #   NOTE もしかすると、繰り上がりが解消しないかもしれないから、循環時に打ち切るよう上限を付けておく
                #
                countdown = 100
                while carried != 0 and 0 < countdown:

                    # ※繰り返し


                    # 説明６　あと何回対局すると、表の得が、裏が出る確率の整数比を上回るか
                    # ---------------------------------------------------------------

                    # あと何対局すると、余りが後手の整数比を上回るか（次の閏対局までの長さ）
                    fill_bouts = math.ceil(w_point / carried)
                    #print(f"\n  一対局毎に余りが{carried}ずつ溜まり、{w_point}以上になるのが、次の閏対局までの長さ{fill_bouts:2}")
                    print(f"(得{carried:2}×{fill_bouts:2}局>=分子{w_point:2})", end='')


                    if carried != 0:
                        for i in range(0, 1):

                            # 次に余りを解消できる閏対局
                            next_leap += fill_bouts
                            #print(f"  次に余りを解消できる閏対局第{next_leap:2}")

                            # 次の繰り上がり先手勝率点
                            carried = b_point % carried
                            #print(f"  次の繰り上がり先手勝率点{carried}")
                            print(f"[第{next_leap:2}](新得{carried:2}) ", end='')

                            if carried == 0:
                                #print(f"  余り解消")
                                print(f"(繰り返し)", end='')
                                break

                            # 繰り上がり込み先手勝率点
                            carryover_b_point = b_point + carried
                            #print(f"  繰り上がり込み先手勝率点{carryover_b_point}")

                    countdown -= 1

            # 繰り上がりがある場合
            if carried != 0:
                #print(f"  （計算未完了）", end='')
                print(f"(計算未完了)", end='')

            print() # 改行


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
