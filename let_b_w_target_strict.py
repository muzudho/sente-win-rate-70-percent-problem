#
# 計算
# python let_b_w_target_strict.py
#
#   先手先取本数、後手先取本数を求める（厳密）
#

import traceback
import datetime
import random
import math

from library import black_win_rate_to_b_w_targets, calculate_probability


SUMMARY_FILE_PATH = 'output/let_b_w_target_strict.log'


# 0.50 < p and p <= 0.99
INPUT_DATA = [
    #[0.50],
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

            # ベストな調整後の先手勝率と、その誤差
            best_balanced_black_win_rate = 101.0
            best_error = 0.51
            best_b_point = 0
            best_w_point = 0

            # 計算過程
            process_list = []

            # p=0.5 は計算の対象外とします
            for b_point in range(1, 1001):

                # 後手に必要な先取本数は 1 に固定します
                for w_point in range (1, 2): # (1, b_point)

                    balanced_black_win_rate = calculate_probability(
                        p=black_win_rate,
                        H=b_point,
                        T=w_point)

                    # 誤差
                    error = abs(balanced_black_win_rate - 0.5)

                    if error < best_error:
                        best_error = error
                        best_balanced_black_win_rate = balanced_black_win_rate
                        best_b_point = b_point
                        best_w_point = w_point
                        process_list.append(f"[{best_error:6.4f} 黒{best_b_point:>3} 白{best_w_point:>2}]")


            with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = f"[{datetime.datetime.now()}]  先手勝率 {black_win_rate*100:2.0f} ％  先取本数　先手：後手＝{best_b_point:>2}：{best_w_point:>2}  調整後先手勝率 {best_balanced_black_win_rate*100:6.4f} ％  誤差 {best_error*100:>7.4f}  {''.join(process_list)}"
                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise