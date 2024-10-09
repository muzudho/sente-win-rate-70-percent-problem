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

from library import calculate_probability, SeriesRule, FROZEN_TURN, OUT_OF_P, ABS_OUT_OF_ERROR
from library.views import stringify_p_q_time_strict
from config import DEFAULT_UPPER_LIMIT_OF_P


LOG_FILE_PATH = 'output/generate_b_q_time_strict.log'

FAILURE_RATE = 0.0
TURN_SYSTEM = FROZEN_TURN

# ［先後固定制］で、［裏勝ちだけでの対局数］の上限
MAX_W_REPEAT_WHEN_FROZEN_TURN = 6 # 99999


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trial_series = 1

        # ［コインを投げて表が出る確率］
        for p_parcent in range(EVEN * 100, DEFAULT_UPPER_LIMIT_OF_P * 100):
            p = p_parcent / 100

            # ベストな調整後の先手勝率と、その誤差
            best_p = None
            best_p_error = ABS_OUT_OF_ERROR
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
                    # オーバーフロー例外に対応したプログラミングをすること
                    latest_theoretical_p, err = calculate_probability(
                            p=p,
                            H=p_time,
                            T=q_time)

                    # FIXME とりあえず、エラーが起こっている場合は、あり得ない値をセットして計算を完了させておく
                    if err is not None:
                        latest_p_error = 0      # 何度計算しても失敗するだろうから、計算完了するようにしておく
                    else:
                        # 誤差
                        latest_theoretical_p_error = abs(latest_theoretical_p - 0.5)

                    if latest_error < best_p_error:
                        best_p_error = latest_theoretical_p_error
                        best_p = latest_theoretical_p
                        best_p_time = p_time
                        best_q_time = q_time

                        # 仕様
                        spec = Specification(
                                turn_system_id=TURN_SYSTEM,
                                failure_rate=failure_rate,
                                p=p)

                        # ［シリーズ・ルール］
                        latest_series_rule = SeriesRule.make_series_rule_base(
                                spec=spec,
                                span=-1, # FIXME データをちゃんと入れたい
                                t_step=-1, # FIXME データをちゃんと入れたい
                                h_step=-1) # FIXME データをちゃんと入れたい

                        candidate_obj = Candidate(
                                p_error=best_p_error,
                                trial_series=specified_trial_series,
                                h_step=latest_series_rule.h_step,
                                t_step=latest_series_rule.t_step,
                                span=latest_series_rule.span,
                                shortest_coins=latest_series_rule.shortest_coins,
                                upper_limit_coins=latest_series_rule.upper_limit_coins)
                        
                        # ［シリーズ・ルール候補］
                        candidate_str = candidate_obj.as_str()
                        candidate_list.append(candidate_str)
                        print(candidate_str, end='', flush=True) # すぐ表示


            # 計算過程の表示の切れ目
            print() # 改行


            with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:

                # 仕様
                spec = Specification(
                        turn_system_id=FROZEN_TURN,
                        failure_rate=FAILURE_RATE,
                        p=p)

                # ［シリーズ・ルール］
                series_rule = SeriesRule.make_series_rule_auto_span(
                    spec=spec,
                    trial_series=specified_trial_series,
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
