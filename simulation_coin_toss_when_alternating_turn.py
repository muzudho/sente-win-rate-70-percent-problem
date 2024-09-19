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
from library import ALICE, CoinToss, PointsConfiguration
from views import stringify_log_when_simulation_coin_toss_when_alternating_turn


LOG_FILE_PATH = 'output/simulation_coin_toss_when_alternating_turn.log'
CSV_FILE_PATH_TSS = './data/takahashi_satoshi_system.csv'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df = pd.read_csv(CSV_FILE_PATH_TSS, encoding="utf8")

        # 対局数
        round_total = 2_000_000 # 十分多いケース
        #round_total = 200

        coin_toss = CoinToss(output_file_path=LOG_FILE_PATH)

        # 先手勝率, 先手の何本先取制, 後手の何本先取制
        for p, b_time, w_time in zip(df['p'], df['b_time'], df['w_time']):

            # ［勝ち点ルール］の構成
            points_configuration = PointsConfiguration.let_points_from_repeat(b_time, w_time)

            # NOTE ［先後固定制］での［勝ち点ルール］の構成をそのまま使うと、先手勝率が 37% ～ 63% にぶれてしまう

            # # NOTE ［先後交互制］では、さらに確率の調整を入れる。 b_time を 4 倍、 w_time を 2 倍にし、さらに約分する ----> さすがに先手勝率が 37% ～ 53% ぐらいに下がってしまう
            #b_time *= 4
            #w_time *= 2
            #fraction = Fraction(w_time, b_time)
            #w_time = fraction.numerator
            #b_time = fraction.denominator

            # # NOTE ［先後交互制］では、さらに確率の調整を入れる。 b_time を 1 増やす ----> 先手勝率が 37% ～ 63% にぶれてしまう
            #b_time += 1


            # Ａさんが勝った回数
            alice_wons = 0

            for round in range(0, round_total):
                round_th = round + 1

                # 勝ったプレイヤーを返す
                winner_player, bout_th = coin_toss.play_game_when_alternating_turn(p, points_configuration)
                if winner_player == ALICE:
                    alice_wons += 1


            # Ａさんが勝った確率
            alice_won_rate = alice_wons / round_total

            # 均等からの誤差
            error = abs(alice_won_rate - 0.5)

            text = stringify_log_when_simulation_coin_toss_when_alternating_turn(p, alice_won_rate, error, b_time, round_total)
            print(text) # 表示

            # ログ出力
            with open(coin_toss.output_file_path, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
