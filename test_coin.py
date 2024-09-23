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

from library import BLACK, WHITE, coin
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

    color = coin(p)

    if color == BLACK:
        text = "表が出た"
    
    elif color == WHITE:
        text = "裏が出た"

    else:
        text = "どちらも出なかった"


    # 表示
    print(text)

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        for i in range(0, 100):
            test_coin(0.5, 0.0)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
