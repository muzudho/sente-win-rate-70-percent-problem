#
# レポート作成
# python report_selection_series_rule.py
#
#   ［表勝ち１つの点数］、［裏勝ち１つの点数］、［目標の点数］をテキストにまとめる。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import HEAD, TAIL, SUCCESSFUL, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, round_letro, calculate_probability, SeriesRule, Specification
from library.database import get_df_selection_series_rule, get_df_selection_series_rule
from library.views import stringify_report_selection_series_rule


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_selection_series_rule.log'

FAILURE_RATE = 0.0

OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


def generate_report(turn_system):

    df_ssr = get_df_selection_series_rule(turn_system=turn_system)

    for             p,           number_of_series,           p_step,           q_step,           span,           presentable,           comment,           candidates in\
        zip(df_ssr['p'], df_ssr['number_of_series'], df_ssr['p_step'], df_ssr['q_step'], df_ssr['span'], df_ssr['presentable'], df_ssr['comment'], df_ssr['candidates']):

        if p_step < 1:
            p_step = 1

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        number_of_series = round_letro(number_of_series)
        p_step = round_letro(p_step)
        q_step = round_letro(q_step)
        span = round_letro(span)

        # ［先後交互制］
        if turn_system == WHEN_ALTERNATING_TURN:

            # ［シリーズ・ルール］。任意に指定します
            specified_series_rule = SeriesRule.make_series_rule_base(
                    failure_rate=FAILURE_RATE,
                    p_step=p_step,
                    q_step=q_step,
                    span=span,
                    turn_system=turn_system)

            # NOTE ［先後交代制］では、理論値の出し方が分からないので、理論値ではなく、実際値をコメントから拾って出力する
            latest_theoretical_p = calculate_probability(
                    p=p,
                    H=specified_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                    T=specified_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))

            # 文言の作成
            text = stringify_report_selection_series_rule(
                    p=p,
                    number_of_series=number_of_series,
                    latest_theoretical_p=latest_theoretical_p,
                    specified_series_rule=specified_series_rule,    # TODO 任意のポイントを指定したい
                    presentable=presentable,
                    candidate=candidate,
                    turn_system=WHEN_ALTERNATING_TURN)
            print(text) # 表示

            with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ログファイルへ出力


        # ［先後固定制］
        elif turn_system == WHEN_FROZEN_TURN:

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    turn_system=WHEN_ALTERNATING_TURN)

            # ［シリーズ・ルール］。任意に指定します
            specified_series_rule = SeriesRule.make_series_rule_base(
                    failure_rate=FAILURE_RATE,
                    p_step=p_step,
                    q_step=q_step,
                    span=span,
                    turn_system=turn_system)

            # NOTE 実際値ではなく、理論値を出力する
            latest_theoretical_p = calculate_probability(
                    p=p,
                    H=specified_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                    T=specified_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))

            # 文言の作成
            text = stringify_report_selection_series_rule(
                    p=p,
                    number_of_series=number_of_series,
                    latest_theoretical_p=latest_theoretical_p,
                    specified_series_rule=specified_series_rule,    # TODO 任意のポイントを指定したい
                    presentable=presentable,
                    candidate=candidate,
                    turn_system=spec.turn_system)
                    
            print(text) # 表示

            with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ログファイルへ出力
            
            return

        else:
            raise ValueError(f"{turn_system=}")


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［先後交互制］
        generate_report(turn_system=WHEN_ALTERNATING_TURN)

        # ［先後固定制］
        generate_report(turn_system=WHEN_FROZEN_TURN)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
