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
    [           0.51,                  49,                  47],
    [           0.52,                  26,                  24],
    [           0.53,                  18,                  16],
    [           0.54,                  14,                  12],
    [           0.55,                  17,                  14],
    [           0.56,                  24,                  19],
    [           0.57,                  25,                  19],
    [           0.58,                  15,                  11],
    [           0.59,                   7,                   5],
    [           0.60,                  60,                  40],
    [           0.61,                  17,                  11],
    [           0.62,                   8,                   5],
    [           0.63,                  27,                  16],
    [           0.64,                  14,                   8],
    [           0.65,                   9,                   5],
    [           0.66,                  21,                  11],
    [           0.67,                  18,                   9],
    [           0.68,                   6,                   3],
    [           0.69,                  24,                  11],
    [           0.70,                  30,                  13],
    [           0.71,                   2,                   1],
    [           0.72,                  20,                   8],
    [           0.73,                  13,                   5],
    [           0.74,                   8,                   3],
    [           0.75,                  44,                  15],
    [           0.76,                  12,                   4],
    [           0.77,                   6,                   2],
    [           0.78,                  17,                   5],
    [           0.79,                   3,                   1],
    [           0.80,                  11,                   3],
    [           0.81,                  16,                   4],
    [           0.82,                   8,                   2],
    [           0.83,                  23,                   5],
    [           0.84,                   4,                   1],
    [           0.85,                  10,                   2],
    [           0.86,                  17,                   3],
    [           0.87,                   5,                   1],
    [           0.88,                  20,                   3],
    [           0.89,                   6,                   1],
    [           0.90,                  42,                   5],
    [           0.91,                  27,                   3],
    [           0.92,                  20,                   2],
    [           0.93,                  23,                   2],
    [           0.94,                  11,                   1],
    [           0.95,                  32,                   2],
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
