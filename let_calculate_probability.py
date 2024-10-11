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
from library.database import CalculateProbabilityTable
from library.views import stringify_calculate_probability


LOG_FILE_PATH = 'output/let_calculate_probability.log'
CSV_FILE_PATH_CAL_P = './data/let_calculate_probability.csv'


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        cp_df, file_read_result = CalculateProbabilityTable.from_csv()
        print(cp_df)

        df = cp_df

        # * `p` - 先手が勝つ確率
        # * `p_time` - ［表勝ちだけでの対局数］
        # * `q_time` - ［裏勝ちだけでの対局数］
        # * `best_p` - 調整後の先手が勝つ確率
        # * `best_p_error` - 調整後の表が出る確率の 0.50 からの差の絶対値です。初期値は ABS_OUT_OF_ERROR
        # * `comment` - この行データの説明
        # 
        for         p,       p_time,       q_time,       best_p,       best_p_error,       comment in\
            zip(df['p'], df['p_time'], df['q_time'], df['best_p'], df['best_p_error'], df['comment']):

            # オーバーフロー例外に対応したプログラミングをすること
            temp_best_p, err = calculate_probability(
                    p=p,
                    H=p_time,
                    T=q_time)

            # FIXME とりあえず、エラーが起こっている場合は、あり得ない値をセットして計算を完了させておく
            if err is not None:
                temp_best_p_error = 0      # 何度計算しても失敗するだろうから、計算完了するようにしておく
            else:
                # 誤差
                temp_best_p_error = temp_best_p - 0.5


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                # 文言作成
                # -------

                text = stringify_calculate_probability(
                        p=p,
                        p_time=p_time,
                        q_time=q_time,
                        best_p=temp_best_p,
                        best_p_error=temp_best_p_error)

                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
