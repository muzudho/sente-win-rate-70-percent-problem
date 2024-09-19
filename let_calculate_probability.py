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
import pandas as pd

from library import calculate_probability
from views import stringify_when_let_calculate_probability


LOG_FILE_PATH = 'output/let_calculate_probability.log'
CSV_FILE_PATH = './data/let_calculate_probability.csv'


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        df = pd.read_csv(CSV_FILE_PATH, encoding="utf8")
        print(df)

        # * `p` - 先手が勝つ確率
        # * `b_time` - ［黒だけでの回数］
        # * `w_time` - ［白だけでの回数］
        # * `new_p` - 調整後の先手が勝つ確率
        # * `new_p_error` - 調整後の表が出る確率の 0.50 からの差の絶対値です。初期値は 0.51
        # * `comment` - この行データの説明
        # 
        for p, b_time, w_time, new_p, new_p_error, comment in zip(df['p'], df['b_time'], df['w_time'], df['new_p'], df['new_p_error'], df['comment']):

            temp_new_p = calculate_probability(
                    p=p,
                    H=b_time,
                    T=w_time)

            # 誤差
            temp_new_p_error = temp_new_p - 0.5


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = stringify_when_let_calculate_probability(p, b_time, w_time, temp_new_p, temp_new_p_error)

                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
