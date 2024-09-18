#
# NOTE この計算は間違っている。累積二項分布を使う必要がある
#
# 計算
# python let_b_w_target_rough.py
#
#   先手先取本数、後手先取本数を求める（正確ではない）
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import black_win_rate_to_b_w_targets


LOG_FILE_PATH = 'output/let_b_w_target_rough.log'

# 下の式になるような、先手先取本数、後手先取本数を求めたい。
#
#
# 　　　　   先手先取本数
# ───────────────────────────────　＝　先手勝率
# 　先手先取本数　＋　後手先取本数
#
# ここで、先手先取本数、後手先取本数は１以上の整数とし、先手先取本数　≧　後手先取本数。
#
#
# 例：
#
# 　　　７
# ─────────────　＝　０．７
# 　７　＋　３
#
#
# このような数式はすぐに作れる。例えば　先手勝率０．６５なら、
#
# 　　　 ６５
# ─────────────────　＝　０．６５
# 　６５　＋　３５


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df = pd.read_csv("./data/p.csv", encoding="utf8")

        # 先手勝率
        for p in df['p']:
            b_point, w_point = black_win_rate_to_b_w_targets(p=p)

            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = f"[{datetime.datetime.now()}]  先手勝率：{p:4.2f}  先取本数　黒：白＝{b_point:>2}：{w_point:>2}"
                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
