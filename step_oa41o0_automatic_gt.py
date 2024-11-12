#
# python step_oa41o0_automatic_gt.py
#
#   * `gt`` - game tree
#
#   １シリーズのコインの出目について、全パターン網羅した樹形図をCSV形式で出力します。
#   レコードは可変列です
#

import traceback
import os
import random
import time
import datetime
import xltree as tr

from library import HEAD, TAIL, FROZEN_TURN, ALTERNATING_TURN, Converter, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths, GameTreeCheckedFilePaths
from library.database import GameTreeTable
from library.views import PromptCatalog
from library.score_board import search_all_score_boards
from scripts import SaveOrIgnore, ForEachSpec
from scripts.step_oa41o1o0_gt import GeneratorOfGT
from config import DEFAULT_UPPER_LIMIT_FAILURE_RATE, DEFAULT_UPPER_LIMIT_SPAN


class Automatic():


    @staticmethod
    def get_series_rule_at_random():
        # ［先後の決め方］
        turn_system_id = turn_system_id_list[random.randint(0, len(turn_system_id_list) - 1)]

        # ［将棋の引分け率］
        failure_rate = feature_rate_list[random.randint(0, len(feature_rate_list) - 1)]

        # ［将棋の先手勝率］
        p = p_list[random.randint(0, len(p_list) - 1)]

        # ［目標の点数］
        #span = random.randint(1, DEFAULT_UPPER_LIMIT_SPAN)
        #span = random.randint(1, 15)   # 15, 16
        span = random.randint(1, 13)    # FIXME 自動最適化できるか？ 18は15秒でもタイムアウトする

        t_step = random.randint(1, span)

        h_step = random.randint(1, t_step)

        print(f"[{datetime.datetime.now()}] step {Converter.turn_system_id_to_name(turn_system_id)}  {failure_rate=}  {p=}  {span=}  {t_step=}  {h_step=}")


        # 仕様
        spec = Specification(
                turn_system_id=turn_system_id,
                failure_rate=failure_rate,
                p=p)


        # ［シリーズ・ルール］。任意に指定します
        series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                span=span,
                t_step=t_step,
                h_step=h_step)


        return series_rule


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        turn_system_id_list = [ALTERNATING_TURN, FROZEN_TURN]
        #print(f"{turn_system_id_list=}")

        # 5％刻み。 100%は除く。0除算が発生するので
        feature_rate_list = list(map(lambda x: x/100, range(0, int(DEFAULT_UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5)))
        #print(f"{feature_rate_list=}")

        p_list = list(map(lambda x: x/100, range(50, 96)))
        #print(f"{p_list=}")


        # 無限ループ
        while True:

            # 0.1秒休む
            time.sleep(0.1)

            series_rule = Automatic.get_series_rule_at_random()


            # ファイルパス取得
            # ---------------
            checked_csv_file_path = GameTreeCheckedFilePaths.as_csv(    # チェック済CSV
                    spec=series_rule.spec,
                    span=series_rule.span,
                    t_step=series_rule.t_step,
                    h_step=series_rule.h_step)
            
            csv_file_path = GameTreeFilePaths.as_csv(       # CSV
                    spec=series_rule.spec,
                    span=series_rule.span,
                    t_step=series_rule.t_step,
                    h_step=series_rule.h_step)


            # チェック済に存在したらスキップ
            if os.path.isfile(checked_csv_file_path):
                continue

            # 存在したらスキップ
            if os.path.isfile(csv_file_path):
                continue


            # 存在しなければ作成
            # ----------------

            forest = tr.planting()
            root_entry = forest.tree_root(edge_text=None, node_text='1')

            generator_of_gt = GeneratorOfGT(spec=series_rule.spec, root_entry=root_entry)

            # FIXME 時間がかかる？
            print(f"[{datetime.datetime.now()}] step_oa41o0_automatic_gt get score board (2) ...")
            #timeout = tr.timeout(seconds=7) # 7, 15, 60
            timeout = tr.timeout(seconds=6)    # FIXME 自動最適化できるか？
            result = search_all_score_boards(
                    series_rule=series_rule,
                    on_score_board_created=generator_of_gt.on_score_board_created,
                    timeout=timeout)
            print(f"[{datetime.datetime.now()}] got score board")


            if timeout.is_expired('get score board (2)'):
                print(f"[{datetime.datetime.now()}] time-out. {timeout.message}")

            else:
                # CSVファイル出力（追記）
                result = forest.to_csv(csv_file_path=csv_file_path, timeout=timeout)

                if timeout.is_expired('get score board (2b)'):
                    print(f"[{datetime.datetime.now()}] time-out. {timeout.message}")

                else:
                    print(f"[{datetime.datetime.now()}] please look {csv_file_path}")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
