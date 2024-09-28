#
# NOTE 使ってない
#
# 生成
# python generate_b_q_time_strict.py
#
#   先後固定制で、［表勝ちだけでの対局数］、［裏勝ちだけでの対局数］を求める（厳密）
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import calculate_probability, SeriesRule, WHEN_FROZEN_TURN
from library.database import get_df_p
from library.views import stringify_p_q_time_strict


LOG_FILE_PATH = 'output/generate_b_q_time_strict.log'

FAILURE_RATE = 0.0
TURN_SYSTEM = WHEN_FROZEN_TURN

# ［先後固定制］で、［裏勝ちだけでの対局数］の上限
MAX_W_REPEAT_WHEN_FROZEN_TURN = 6 # 99999

OUT_OF_ERROR = 0.51


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        df = get_df_p()

        # ［コインを投げて表が出る確率］
        for p in df['p']:

            # ベストな調整後の先手勝率と、その誤差
            best_p = None
            best_p_error = OUT_OF_ERROR
            best_p_time = 0
            best_q_time = 0

            # ［シリーズ・ルール候補］
            candidate_list = []

            # p=0.5 は計算の対象外とします
            for p_time in range(1, 101):

                # ［先後固定制］で、［裏勝ちだけでの対局数］の上限
                max_q_time = p_time
                if MAX_W_REPEAT_WHEN_FROZEN_TURN < max_q_time:
                    max_q_time = MAX_W_REPEAT_WHEN_FROZEN_TURN                

                for q_time in range (1, max_q_time+1):

                    # 理論値
                    latest_theoretical_p = calculate_probability(
                            p=p,
                            H=p_time,
                            T=q_time)

                    # 誤差
                    latest_theoretical_p_error = abs(latest_theoretical_p - 0.5)

                    if latest_error < best_p_error:
                        best_p_error = latest_theoretical_p_error
                        best_p = latest_theoretical_p
                        best_p_time = p_time
                        best_q_time = q_time

                        # 仕様
                        spec = Specification(
                                p=p,
                                failure_rate=failure_rate,
                                turn_system=FAILURE_RATE)

                        # ［シリーズ・ルール］
                        # TODO データをちゃんと入れたい
                        latest_series_rule = SeriesRule.make_series_rule_base(
                                failure_rate=spec.failure_rate,
                                # FIXME タイムではなくステップが欲しい
                                p_step=-1,
                                q_step=-1,
                                span=-1,
                                turn_system=spec.turn_system)

                        candidate_obj = Candidate(
                                p_error=best_p_error,
                                number_of_series=1, # FIXME
                                p_step=latest_series_rule.p_step,
                                q_step=latest_series_rule.q_step,
                                span=latest_series_rule.span,
                                number_of_shortest_time=latest_series_rule.number_of_shortest_time,
                                longest_coins=latest_series_rule.longest_coins)
                        
                        # ［シリーズ・ルール候補］
                        candidate_str = candidate_obj.as_str()
                        candidate_list.append(candidate_str)
                        print(candidate_str, end='', flush=True) # すぐ表示


            # 計算過程の表示の切れ目
            print() # 改行


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:

                # ［シリーズ・ルール］
                series_rule = SeriesRule.make_series_rule_auto_span(
                    failure_rate=FAILURE_RATE,
                    turn_system=WHEN_FROZEN_TURN,
                    p_time=best_p_time,
                    q_time=best_q_time)

                text = stringify_p_q_time_strict(
                        p=p,
                        best_p=best_p,
                        best_p_error=best_p_error,
                        series_rule=series_rule,
                        candidate_list=candidate_list)

                print(text) # 表示

                f.write(f"{text}\n")    # ファイルへ出力


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
