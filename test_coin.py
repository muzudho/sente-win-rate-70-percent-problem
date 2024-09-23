#
# テスト
# python test_coin.py
#
#   コインについて、指定の表が出る確率、裏が出る確率、どちらでもない確率がだいたい出るかテストする
#

import traceback
import random
import math

import pandas as pd

from library import HEAD, TAIL, coin
from database import get_df_muzudho_single_points_when_frozen_turn
from views import stringify_series_log, stringify_analysis_series_when_frozen_turn


LOG_FILE_PATH = 'output/test_coin.log'


def test_coin(p, draw_rate):
    """コインについて、指定の表が出る確率、裏が出る確率、どちらでもない確率がだいたい出るかテストする
    
    Parameters
    ----------
    p : float
        ［表が出る確率］
    draw_rate : float
        ［将棋の引分け率］
    """

    return coin(p)


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        number_of_black = 0     # 表が出た回数
        number_of_white = 0     # 裏が出た回数
        number_of_draw = 0      # 表も裏も出なかった回数

        for i in range(0, 100):
            color = test_coin(0.5, 0.0)

            if color == HEAD:
                text = "表が出た"
                number_of_black += 1
            
            elif color == TAIL:
                text = "裏が出た"
                number_of_white += 1

            else:
                text = "どちらも出なかった"
                number_of_draw += 1

            # 表示
            print(text)

            # ファイルへログ出力
            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")


        text = f"""\
{text}
表が出た回数：          {number_of_black}
裏が出た回数：          {number_of_white}
表も裏も出なかった回数： {number_of_draw}
"""

        # 表示
        print(text)
  
        # ファイルへログ出力
        with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
            f.write(f"{text}\n")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
