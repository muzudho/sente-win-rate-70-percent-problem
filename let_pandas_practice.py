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


        for p, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn in zip(df['p'], df['b_repeat_when_frozen_turn'], df['w_repeat_when_frozen_turn']):
            print(f"{p=}  {b_repeat_when_frozen_turn=}  {w_repeat_when_frozen_turn}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
