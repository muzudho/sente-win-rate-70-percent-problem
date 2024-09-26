# Pandas の練習
# python let_pandas_practice.py

import traceback
import pandas as pd

from library.database import get_df_report_selection_series_rule


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_ssr = get_df_report_selection_series_rule()
        print(df_ssr)


        for column_name in df_ssr:
            print(f"{column_name=}")


        for p, p_time, q_time in zip(df_ssr['p'], df_ssr['p_time'], df_ssr['q_time']):
            print(f"{p=}  {p_time=}  {q_time}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
