#
# シミュレーション
# python simulation_coin_toss_when_frozen_turn.py
#
#   ［先後固定制］
#   引き分けは考慮していない。
#   表が出る確率（p）が偏ったコインを、指定回数（max_number_of_bout_when_frozen_turn）投げる
#

import traceback
import random
import math

import pandas as pd

from library import BLACK, CoinToss
from views import stringify_log_when_simulation_coin_toss_when_frozen_turn


LOG_FILE_PATH = 'output/simulation_coin_toss_when_frozen_turn.log'
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
        #round_total = 10 # 少なすぎるケース

        # 先手勝率, 先手の何本先取制, 後手の何本先取制
        for p, b_time, w_time in zip(df['p'], df['b_time'], df['w_time']):
            coin_toss = CoinToss(output_file_path=LOG_FILE_PATH)

            # 黒が勝った回数
            black_wons = 0

            for round in range(0, round_total):
                # 勝った方の手番を返す
                if coin_toss.coin_toss_in_round(p, b_time, w_time) == BLACK:
                    black_wons += 1


            text = stringify_log_when_simulation_coin_toss_when_frozen_turn(
                    # 出力先ファイルへのパス
                    output_file_path=coin_toss.output_file_path,
                    # 先手勝率
                    black_win_rate=p,
                    # 先手の何本先取制
                    b_time=b_time,
                    # 後手の何本先取制
                    w_time=w_time,
                    # 対局数
                    round_total=round_total,
                    # 黒が勝った回数
                    black_wons=black_wons)

            print(text) # 表示

            # ログ出力
            with open(output_file_path, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
