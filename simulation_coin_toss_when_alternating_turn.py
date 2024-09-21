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
from database import get_def_report_muzudho_recommends_points
from views import stringify_log_when_simulation_coin_toss_when_alternating_turn


LOG_FILE_PATH = 'output/simulation_coin_toss_when_alternating_turn.log'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df_mrp = get_def_report_muzudho_recommends_points()

        # 対局数
        round_total = 2_000_000 # 十分多いケース
        #round_total = 200

        # 先手勝率, 先手の何本先取制, 後手の何本先取制
        for             p,           b_time,           w_time in\
            zip(df_mrp['p'], df_mrp['b_time'], df_mrp['w_time']):

            # ［かくきんシステムのｐの構成］
            points_configuration = PointsConfiguration.let_points_from_repeat(
                    b_time=b_time,
                    w_time=w_time)

            # Ａさんが勝った回数
            alice_wons = 0

            for round in range(0, round_total):
                round_th = round + 1

                # 勝ったプレイヤーを返す
                winner_player, bout_th = play_game_when_alternating_turn(p, points_configuration)
                if winner_player == ALICE:
                    alice_wons += 1


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


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
