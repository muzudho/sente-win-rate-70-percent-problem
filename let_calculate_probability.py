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
        # * `b_repeat_when_frozen_turn` - ［黒だけでの反復数］
        # * `w_repeat_when_frozen_turn` - ［白だけでの反復数］
        # * `new_p` - 調整後の先手が勝つ確率
        # * `new_p_error` - 調整後の表が出る確率の 0.50 からの差の絶対値です。初期値は 0.51
        # * `comment` - この行データの説明
        # 
        for p, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn, new_p, new_p_error, comment in zip(df['p'], df['b_repeat_when_frozen_turn'], df['w_repeat_when_frozen_turn'], df['new_p'], df['new_p_error'], df['comment']):

            balanced_black_win_rate = calculate_probability(
                p=p,
                H=b_repeat_when_frozen_turn,
                T=w_repeat_when_frozen_turn)

            # 誤差
            error = balanced_black_win_rate - 0.5


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = stringify_when_let_calculate_probability(p, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn, balanced_black_win_rate, error)

                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
