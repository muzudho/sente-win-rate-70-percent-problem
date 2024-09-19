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
from views import write_coin_toss_log


LOG_FILE_PATH = 'output/simulation_coin_toss_when_frozen_turn.log'
CSV_FILE_PATH = './data/takahashi_satoshi_system.csv'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df = pd.read_csv(CSV_FILE_PATH, encoding="utf8")

        # 対局数
        round_total = 2_000_000 # 十分多いケース
        #round_total = 10 # 少なすぎるケース

        # 先手勝率, 先手の何本先取制, 後手の何本先取制
        for p, b_repeat, w_repeat in zip(df['p'], df['b_repeat'], df['w_repeat']):
            coin_toss = CoinToss(output_file_path=LOG_FILE_PATH)

            # 黒が勝った回数
            black_wons = 0

            for round in range(0, round_total):
                # 勝った方の手番を返す
                if coin_toss.coin_toss_in_round(p, b_repeat, w_repeat) == BLACK:
                    black_wons += 1


            # ログ出力
            write_coin_toss_log(
                    # 出力先ファイルへのパス
                    output_file_path=coin_toss.output_file_path,
                    # 先手勝率
                    black_win_rate=p,
                    # 先手の何本先取制
                    b_repeat=b_repeat,
                    # 後手の何本先取制
                    w_repeat=w_repeat,
                    # 対局数
                    round_total=round_total,
                    # 黒が勝った回数
                    black_wons=black_wons)

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
