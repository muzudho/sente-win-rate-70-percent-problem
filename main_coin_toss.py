#
# シミュレーション
# python main_coin_toss.py
#
#   表の出る確率（black_win_rate）が偏ったコインを、指定回数（max_bout_count）投げる
#

import traceback
import datetime
import random
import math

from library import BLACK, WHITE, coin, n_bout, n_round, round_letro


SUMMARY_FILE_PATH = 'main_coin_toss.log'


class CoinToss():
    """コイントスの試行"""


    def __init__(self, summary_file_path):
        """初期化
        
        Parameters
        ----------
        summary_file_path : str
            結果の出力ファイルへのパス
        """
        self._summary_file_path = summary_file_path


    def coin_toss_in_some_rounds(self, black_win_rate, black_target_in_bout, white_target_in_bout, round_total):
        """コイントスを複数対局する
        
        Parameters
        ----------
        black_win_rate : float
            黒が出る確率（先手勝率）
        black_target_in_bout : int
            先手の何本先取制
        white_target_in_bout : int
            後手の何本先取制
        round_total : int
            対局数
        """

        # 初期値
        # ------

        # 黒が勝った回数
        black_wons = 0


        for round in range(0, round_total):

            # 新しい本目（Bout）
            b_count_in_bout = 0
            w_count_in_bout = 0

            # ｎ本勝負で勝ち負けが出るまでやる
            while True:

                # 黒が出た
                if coin(black_win_rate) == BLACK:
                    b_count_in_bout += 1
                
                # 白が出た
                else:
                    w_count_in_bout += 1

                # 黒の先取本数を取った（黒が勝った）
                if black_target_in_bout <= b_count_in_bout:
                    black_wons += 1
                    break

                # 白の先取本数を取った（白が勝った）
                elif white_target_in_bout <= w_count_in_bout:
                    break


        with open(self._summary_file_path, 'a', encoding='utf8') as f:
            # 文言作成
            # -------

            # 黒が勝った確率
            black_won_rate = black_wons / round_total

            text = f"[{datetime.datetime.now()}]  先手勝率：{black_win_rate:4.02f}  先手{black_target_in_bout:2}本先取/後手{white_target_in_bout:2}本先取制  黒勝ち数{black_wons:7}／{round_total:7}対局試行  黒が勝った確率{black_won_rate:8.4f} ％"
            print(text) # 表示
            f.write(f"{text}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        CoinToss(
            summary_file_path=SUMMARY_FILE_PATH).coin_toss_in_some_rounds(
                # 先手勝率
                black_win_rate=0.65,
                # 先手の何本先取制
                black_target_in_bout=9,
                # 後手の何本先取制
                white_target_in_bout=5,
                # 対局数
                round_total=2_000_000)
            #black_target_in_bout = 3   # NOTE 先手勝率80% なら、黒の４本先取より、黒の３本先取の方が勝率５割に近い

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
