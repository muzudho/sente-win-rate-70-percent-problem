# Pandas の練習
# python let_pandas_practice.py

import traceback
import pandas as pd

from database import get_df_report_muzudho_recommends_points


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mrp = get_df_report_muzudho_recommends_points()
        print(df_mrp)


        for column_name in df_mrp:
            print(f"{column_name=}")


        for p, b_time, w_time in zip(df_mrp['p'], df_mrp['b_time'], df_mrp['w_time']):
            print(f"{p=}  {b_time=}  {w_time}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
