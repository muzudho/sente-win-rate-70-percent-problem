#
# 計算
# python let_calculate_probability.py
#
#   確率の試算
#

import traceback
import datetime
import random
import math

from library import calculate_probability


SUMMARY_FILE_PATH = 'output/let_calculate_probability.log'


INPUT_DATA = [
    # black_win_rate  b_point             w_point             balanced_black_win_rate  error     comment
    # 先手が勝つ確率   先手の必要な先取本数  後手の必要な先取本数  調整後の先手が勝つ確率     誤差      説明
    # --------------  ------------------  ------------------  -----------------------  --------  -------

    [           0.65,                 65,                 35, 0.4916                 , -0.0084 , '単純分数'],
    [           0.65,                 13,                  5, 0.2348                 , -0.2652 , '実践値'],

    [           0.7 ,                  7,                  3, 0.4628                 , -0.0372 , '単純分数'],
    [           0.7 ,                  2,                  1, 0.4900                 , -0.0100 , '実践値'],

    [           0.79,                 79,                 21, 0.4810                 , -0.0190 , '単純分数'],
    [           0.79,                  3,                  1, 0.4930                 , -0.0070 , '実践値'],

    [           0.84,                 84,                 16, 0.4753                 , -0.0247 , '単純分数'],
    [           0.84,                  4,                  1, 0.4979                 , -0.0021 , '実践値'],

    [           0.87,                 87,                 13, 0.4707                 , -0.0293 , '単純分数'],
    [           0.87,                  5,                  1, 0.4984                 , -0.0016 , '実践値'],

    [           0.89,                 89,                 11, 0.4668                 , -0.0332 , '単純分数'],
    [           0.89,                  6,                  1, 0.4970                 , -0.0030 , '実践値'],
]


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for input_datum in INPUT_DATA:
            # 先手が勝つ確率
            black_win_rate = input_datum[0]

            # 先手の必要な先取本数
            b_point = input_datum[1]

            # 後手の必要な先取本数
            w_point = input_datum[2]

            balanced_black_win_rate = calculate_probability(
                p=black_win_rate,
                H=b_point,
                T=w_point)

            # 誤差
            error = balanced_black_win_rate - 0.5


            with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = f"[{datetime.datetime.now()}]  先手勝率 {black_win_rate:4.2f}  先取本数　先手：後手＝{b_point:>2}：{w_point:>2}  調整後の先手勝率 {balanced_black_win_rate:6.4f}  誤差{error:7.4f}"
                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
