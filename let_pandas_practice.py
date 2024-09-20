# Pandas の練習
# python let_pandas_practice.py

import traceback
import pandas as pd


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_even = pd.read_csv("./data/report_evenizing_system.csv", encoding="utf8")

        print(df_even)


        for column_name in df_even:
            print(f"{column_name=}")


        for p, b_time, w_time in zip(df_even['p'], df_even['b_time'], df_even['w_time']):
            print(f"{p=}  {b_time=}  {w_time}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
