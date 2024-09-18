#
# NOTE ［閏対局］は今のところ没案
#
# シミュレーション
# python simulation_coin_toss_with_leap.py
#
#   閏対局のシミュレーション
#

import traceback
import datetime
import random
import math

from library import BLACK, round_letro, black_win_rate_to_b_w_targets, CoinToss


LOG_FILE_PATH = 'output/simulation_coin_toss_with_leap.log'


INPUT_DATA = [
    # black_win_rate  leap_th_list
    # 先手勝率         閏対局リスト
    # --------------  ------------
    [           0.50, []],
    [           0.51, [25, 74]],
    [           0.52, [12]],
    [           0.53, [8, 18, 34,58, 105]],
    [           0.54, [6, 14]],
    [           0.55, [5, 14]],
    [           0.56, [4, 10]],
    [           0.57, [4, 47]],
    [           0.58, [3, 8, 14, 35]],
    [           0.59, [5, 8, 14, 35]],
    [           0.60, [2]],
    [           0.61, [2, 5, 9, 48]],
    [           0.62, [2, 5, 12, 31]],
    [           0.63, [2, 6, 11, 17]],
    [           0.64, [2, 7]],
    [           0.65, [2, 9]],
    [           0.66, [2, 19]],
    [           0.67, [33]],
    [           0.68, [8]],
    [           0.69, [5, 11, 22]],
    [           0.70, [3]],
    [           0.71, [3, 8, 14, 43]],
    [           0.72, [2, 6]],
    [           0.73, [2, 4, 7, 34]],
    [           0.74, [2, 6, 19]],
    [           0.75, []],
    [           0.76, [6]],
    [           0.77, [3, 8, 20, 43]],
    [           0.78, [2, 6]],
    [           0.79, [2, 4, 10, 17, 38]],
    [           0.80, []],
    [           0.81, [4, 23]],
    [           0.82, [2, 11]],
    [           0.83, [2, 5, 11, 37]],
    [           0.84, [4]],
    [           0.85, [2, 5]],
    [           0.86, [7]],
    [           0.87, [2, 5, 10]],
    [           0.88, [3]],
    [           0.89, [11]],
    [           0.90, []],
    [           0.91, [9]],
    [           0.92, [2]],
    [           0.93, [4, 11]],
    [           0.94, [2, 5]],
    [           0.95, []],
    [           0.96, []],
    [           0.97, [3]],
    [           0.98, []],
    [           0.99, []],
]


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for input_datum in INPUT_DATA:
            coin_toss = CoinToss(output_file_path=LOG_FILE_PATH)

            # 先手勝率
            black_win_rate=input_datum[0]
            print(f"先手勝率{black_win_rate:4.2f}  ")

            # 閏対局のリスト
            leap_th_list = input_datum[1]
            print(f"閏対局{leap_th_list=}  ")

            # 閏対局の周期
            if len(leap_th_list) == 0:
                cycle = 0
            else:
                cycle = leap_th_list[-1]

            print(f"周期{cycle:>2}")


            # 厳密な値
            strict_b_require, strict_w_require = black_win_rate_to_b_w_targets(p=black_win_rate)
            print(f"厳密な先取本数  先手：後手＝{strict_b_require:>2}：{strict_w_require:>2}  ", end='')

            # 実用的な値（後手取得本数が１になるよう丸めたもの）
            practical_b_require = round_letro(strict_b_require / strict_w_require) # 小数点以下四捨五入
            practical_w_require = 1
            print(f"実用的な先取本数  先手：後手＝{practical_b_require:>2}：{practical_w_require:>2}  ", end='')

            print() # 改行

            # 対局数
            round_total = 1_000

            # 黒が勝った回数
            black_wons = 0

            for round in range(0, round_total):
                # TODO 閏対局を入れたパターンと、入れないパターンの比較
                if True:
                    if cycle == 0:
                        round_in_cycle = 0
                    else:
                        round_in_cycle = round % cycle

                    if round_in_cycle + 1 in leap_th_list:
                        # 閏対局
                        # 勝った方の手番を返す
                        if BLACK == coin_toss.coin_toss_in_round(
                                # 先手勝率
                                black_win_rate=black_win_rate,
                                # 先手の何本先取制
                                b_require=practical_b_require + 1,
                                # 後手の何本先取制
                                w_require=practical_w_require):
                            black_wons += 1

                    else:
                        # 閏対局を使わないパターン
                        # 勝った方の手番を返す
                        if BLACK == coin_toss.coin_toss_in_round(
                                # 先手勝率
                                black_win_rate=black_win_rate,
                                # 先手の何本先取制
                                b_require=practical_b_require,
                                # 後手の何本先取制
                                w_require=practical_w_require):
                            black_wons += 1

                # 閏対局を使わないパターン
                else:
                    # 勝った方の手番を返す
                    if BLACK == coin_toss.coin_toss_in_round(
                            # 先手勝率
                            black_win_rate=black_win_rate,
                            # 先手の何本先取制
                            b_require=practical_b_require,
                            # 後手の何本先取制
                            w_require=practical_w_require):
                        black_wons += 1

            # 黒が勝った確率
            black_won_rate = black_wons / round_total

            # 均等からの誤差
            error = abs(black_won_rate - 0.5)

            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                text = f"[{datetime.datetime.now()}]  先手勝率：{black_win_rate:4.02f}  実用的な先手{practical_b_require:2}本先取／後手{practical_w_require:2}本先取制  先手勝ち数{black_wons:7}／{round_total:7}対局試行  先手が勝った確率{black_won_rate*100:8.4f} ％  誤差{error*100:8.4f} ％"
                print(text)
                f.write(f"{text}\n")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
