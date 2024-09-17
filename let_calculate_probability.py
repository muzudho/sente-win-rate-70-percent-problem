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


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # 表が出る確率
        black_win_rate = 0.7

        # 先手の先取本数
        b_point = 7

        # 後手の先取本数
        w_point = 3

        balanced_black_win_rate = calculate_probability(
            p=black_win_rate,
            H=b_point,
            T=w_point)


        with open(SUMMARY_FILE_PATH, 'a', encoding='utf8') as f:
            # 文言作成
            # -------

            text = f"[{datetime.datetime.now()}]  先手勝率：{black_win_rate:4.2f}  先取本数　先手：後手＝{b_point:>2}：{w_point:>2}  調整後の先手勝率：{balanced_black_win_rate:6.4f}"
            print(text) # 表示
            f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
