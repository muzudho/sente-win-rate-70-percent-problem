#
# シミュレーション 手番を交互にするパターン
# python simulation_coin_toss_when_alternating_turn.py
#
#   表の出る確率（black_win_rate）が偏ったコインを、指定回数（max_number_of_bout_when_frozen_turn）投げる
#   Ａさん（Alice）とＢさん（Bob）の勝率を五分五分にする。Ａさんの先手から始める。
#   引き分けは考慮していない。
#

import traceback
import random
import math
import datetime
import pandas as pd

from library import ALICE, CoinToss


LOG_FILE_PATH = 'output/simulation_coin_toss_when_alternating_turn.log'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # 対局数
        round_total = 200

        df = pd.read_csv("./data/takahashi_satoshi_system.csv", encoding="utf8")

        # 先手勝率, 先手の何本先取制, 後手の何本先取制
        for p, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn in zip(df['p'], df['b_repeat_when_frozen_turn'], df['w_repeat_when_frozen_turn']):
            coin_toss = CoinToss(output_file_path=LOG_FILE_PATH)

            # Ａさんが勝った回数
            alice_wons = 0

            for round in range(0, round_total):
                round_th = round + 1

                # 勝ったプレイヤーを返す
                if coin_toss.coin_toss_in_round_when_alternating_turn(p, b_repeat_when_frozen_turn, w_repeat_when_frozen_turn) == ALICE:
                    alice_wons += 1


            # ログ出力
            with open(coin_toss.output_file_path, 'a', encoding='utf8') as f:

                # Ａさんが勝った確率
                alice_won_rate = alice_wons / round_total

                # 均等からの誤差
                error = abs(alice_won_rate - 0.5)

                text = f"[{datetime.datetime.now()}]  先手勝率 {p*100:2.0f} ％ --調整後--> Ａさんが勝った確率{alice_won_rate*100:8.4f} ％（± {error*100:7.4f}）  {b_repeat_when_frozen_turn:2}本勝負  {round_total:7}対局試行"
                print(text) # 表示
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
