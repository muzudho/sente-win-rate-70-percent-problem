#
# シミュレーション
# python simulation_coin_toss_when_alternating_turn.py
#
#   ［先後交互制］
#   引き分けは考慮していない。
#   ［表の出る確率］ p が偏ったコインを、指定回数（max_number_of_bout_when_alternating_turn）投げる
#   Ａさん（Alice）が最初に先手を持ち、１局毎にＢさん（Bob）と先後を交代する。
#

import traceback
import random
import math
import datetime
import pandas as pd

from fractions import Fraction
from library import ALICE, PointsConfiguration, play_game_when_alternating_turn
from database import get_def_muzudho_recommends_points_when_alternating_turn
from views import stringify_log_when_simulation_coin_toss_when_alternating_turn


LOG_FILE_PATH = 'output/simulation_coin_toss_when_alternating_turn.log'


def perform_p(p, round_total, b_time, w_time):

    # ［かくきんシステムのｐの構成］
    points_configuration = PointsConfiguration.let_points_from_repeat(
            b_time=b_time,
            w_time=w_time)

    # Ａさんが勝った回数
    alice_wons = 0
    shortest_bout_th = 2_147_483_647
    longest_bout_th = 0

    for round in range(0, round_total):

        # ［先後交互制］で、勝ったプレイヤーを返す
        winner_player, bout_th = play_game_when_alternating_turn(p, points_configuration)
        if winner_player == ALICE:
            alice_wons += 1

        if bout_th < shortest_bout_th:
            shortest_bout_th = bout_th
        
        if longest_bout_th < bout_th:
            longest_bout_th = bout_th


    # Ａさんが勝った確率
    alice_won_rate = alice_wons / round_total

    # 均等からの誤差
    error = abs(alice_won_rate - 0.5)

    text = stringify_log_when_simulation_coin_toss_when_alternating_turn(
            p=p,
            alice_won_rate=alice_won_rate,
            specified_p_error=error,
            b_time=b_time,
            round_total=round_total)

    print(text) # 表示

    # ログ出力
    with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:
        f.write(f"{text}\n")    # ファイルへ出力

    # # 表示とログ出力を終えた後でテスト
    # if actual_shortest_bout_th_when_alternating_turn < expected_shortest_bout_th_when_alternating_turn:
    #     raise ValueError(f"{p=} ［先後交互制］の最短対局数の実際値 {actual_shortest_bout_th_when_alternating_turn} が理論値 {expected_shortest_bout_th_when_alternating_turn} を下回った")

    # if expected_longest_bout_th_when_alternating_turn < actual_longest_bout_th_when_alternating_turn:
    #     raise ValueError(f"{p=} ［先後交互制］の最長対局数の実際値 {actual_longest_bout_th_when_alternating_turn} が理論値 {expected_longest_bout_th_when_alternating_turn} を上回った")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mr_at = get_def_muzudho_recommends_points_when_alternating_turn()

        # 対局数
        round_total = 2_000_000 # 十分多いケース
        #round_total = 200

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_at['p'], df_mr_at['b_step'], df_mr_at['w_step'], df_mr_at['span'], df_mr_at['presentable'], df_mr_at['comment'], df_mr_at['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            perform_p(
                    p=p,
                    round_total=round_total,
                    b_time=specified_points_configuration.b_time,
                    w_time=specified_points_configuration.w_time)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
