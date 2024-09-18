#
# シミュレーション
# python simulation_coin_toss_in_freeze_turn.py
#
#   表の出る確率（black_win_rate）が偏ったコインを、指定回数（max_number_of_bout_in_freeze_turn）投げる
#

import traceback
import random
import math
import pandas as pd

from library import BLACK, CoinToss
from views import write_coin_toss_log


LOG_FILE_PATH = 'output/simulation_coin_toss_in_freeze_turn.log'


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # 対局数
        round_total = 2_000_000 # 十分多いケース
        #round_total = 10 # 少なすぎるケース

        df = pd.read_csv("./data/takahashi_satoshi_system.csv", encoding="utf8")

        # 先手勝率, 先手の何本先取制, 後手の何本先取制
        for p, b_require, w_require in zip(df['p'], df['b_require'], df['w_require']):
            coin_toss = CoinToss(output_file_path=LOG_FILE_PATH)

            # 黒が勝った回数
            black_wons = 0

            for round in range(0, round_total):
                # 勝った方の手番を返す
                if coin_toss.coin_toss_in_round(p, b_require, w_require) == BLACK:
                    black_wons += 1


            # ログ出力
            write_coin_toss_log(
                    # 出力先ファイルへのパス
                    output_file_path=coin_toss.output_file_path,
                    # 先手勝率
                    black_win_rate=p,
                    # 先手の何本先取制
                    b_require=b_require,
                    # 後手の何本先取制
                    w_require=w_require,
                    # 対局数
                    round_total=round_total,
                    # 黒が勝った回数
                    black_wons=black_wons)

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
