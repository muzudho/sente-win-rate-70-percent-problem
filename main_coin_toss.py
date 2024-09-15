#
# シミュレーション
# python main_coin_toss.py
#
#   表の出る確率（black_win_rate）が偏ったコインを、指定回数（max_bout_count）投げる
#

import traceback
import datetime
import random
import math

from library import CoinToss


SUMMARY_FILE_PATH = 'main_coin_toss.log'


# 連続コイントス
INPUT_DATA = [
    # black_win_rate black_target_in_bout white_target_in_bout
    # 先手勝率        先手の何本先取制      後手の何本先取制
    # -------------- -------------------- --------------------
    [           0.50,                   1,                   1],
    [           0.51,                   1,                   1],
    [           0.52,                  25,                  23],
    [           0.53,                  31,                  15],
    [           0.54,                  25,                  12],
    [           0.55,                  19,                   9],
    [           0.56,                  17,                   8],
    [           0.57,                  29,                  13],
    [           0.58,                  25,                  11],
    [           0.59,                  11,                   5],
    [           0.60,                  34,                  14],
    [           0.61,                   9,                   4],
    [           0.62,                  12,                   5],
    [           0.63,                  23,                   9],
    [           0.64,                   7,                   3],
    [           0.65,                  13,                   5],
    [           0.66,                  25,                   9],
    [           0.67,                  20,                   7],
    [           0.68,                   8,                   3],
    [           0.69,                   5,                   2],
    [           0.70,                   2,                   1],
    [           0.71,                   2,                   1],
    [           0.72,                  27,                   8],
    [           0.73,                  17,                  13],
    [           0.74,                  10,                   3],
    [           0.75,                  58,                  15],
    [           0.76,                  15,                   4],
    [           0.77,                   7,                   2],
    [           0.78,                  21,                   5],
    [           0.79,                   3,                   1],
    [           0.80,                  13,                   3],
    [           0.81,                  19,                   4],
    [           0.82,                   9,                   2],
    [           0.83,                  27,                   5],
    [           0.84,                   4,                   1],
    [           0.85,                  11,                  10],
    [           0.86,                  19,                   3],
    [           0.87,                   5,                   1],
    [           0.88,                  22,                   3],
    [           0.89,                   6,                   1],
    [           0.90,                  46,                   5],
    [           0.91,                  29,                   3],
    [           0.92,                  21,                   2],
    [           0.93,                  24,                   2],
    [           0.94,                  11,                   1],
    [           0.95,                  33,                   2],
    [           0.96,                  17,                   1],
    [           0.97,                  23,                   1],
    [           0.98,                  34,                   1],
    [           0.99,                  67,                   1],
]

#black_target_in_bout = 3   # NOTE 先手勝率80% なら、黒の４本先取より、黒の３本先取の方が勝率５割に近い


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for input_datum in INPUT_DATA:
            CoinToss(
                summary_file_path=SUMMARY_FILE_PATH).coin_toss_in_some_rounds(
                    # 先手勝率
                    black_win_rate=input_datum[0],
                    # 先手の何本先取制
                    black_target_in_bout=input_datum[1],
                    # 後手の何本先取制
                    white_target_in_bout=input_datum[2],
                    # 対局数
                    round_total=2_000_000)

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
