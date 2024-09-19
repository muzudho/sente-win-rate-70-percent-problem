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
        df = pd.read_csv("./data/takahashi_satoshi_system.csv", encoding="utf8")

        print(df)


        for column_name in df:
            print(f"{column_name=}")


        for p, b_time, w_time in zip(df['p'], df['b_time'], df['w_time']):
            print(f"{p=}  {b_time=}  {w_time}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
