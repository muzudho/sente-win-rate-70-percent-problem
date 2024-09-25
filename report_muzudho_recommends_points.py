#
# レポート作成
# python report_muzudho_recommends_points.py
#
#   ［表勝ち１つの点数］、［裏勝ち１つの点数］、［目標の点数］をテキストにまとめる。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, round_letro, calculate_probability, PointsConfiguration, Specification
from database import get_df_muzudho_recommends_points, get_df_muzudho_recommends_points
from views import stringify_report_muzudho_recommends_points


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_muzudho_recommends_points.log'

FAILURE_RATE = 0.0

OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


def generate_report(turn_system):
    if turn_system == WHEN_ALTERNATING_TURN:
        """［先後交互制］"""

        df_mr = get_df_muzudho_recommends_points(turn_system=WHEN_ALTERNATING_TURN)

        for            p,          number_of_series,          p_step,          q_step,          span,          presentable,          comment,          process in\
            zip(df_mr['p'], df_mr['number_of_series'], df_mr['p_step'], df_mr['q_step'], df_mr['span'], df_mr['presentable'], df_mr['comment'], df_mr['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_pts_conf = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    turn_system=turn_system,
                    p_step=p_step,
                    q_step=q_step,
                    span=span)

            # NOTE ［先後交代制］では、理論値の出し方が分からないので、理論値ではなく、実際値をコメントから拾って出力する
            latest_theoretical_p = calculate_probability(
                    p=p,
                    H=specified_pts_conf.p_time,
                    T=specified_pts_conf.q_time)

            # 文言の作成
            text = stringify_report_muzudho_recommends_points(
                    p=p,
                    number_of_series=number_of_series,
                    latest_theoretical_p=latest_theoretical_p,
                    specified_pts_conf=specified_pts_conf,    # TODO 任意のポイントを指定したい
                    presentable=presentable,
                    process=process,
                    turn_system=WHEN_ALTERNATING_TURN)
            print(text) # 表示

            with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ログファイルへ出力

        return

    if turn_system == WHEN_FROZEN_TURN:
        """［先後固定制］"""

        df_mr = get_df_muzudho_recommends_points(turn_system=WHEN_FROZEN_TURN)

        for            p,          number_of_series,          p_step,          q_step,          span,          presentable,          comment,          process in\
            zip(df_mr['p'], df_mr['number_of_series'], df_mr['p_step'], df_mr['q_step'], df_mr['span'], df_mr['presentable'], df_mr['comment'], df_mr['process']):

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    turn_system=WHEN_ALTERNATING_TURN)

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_pts_conf = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    turn_system=turn_system,
                    p_step=p_step,
                    q_step=q_step,
                    span=span)

            # NOTE 実際値ではなく、理論値を出力する
            latest_theoretical_p = calculate_probability(
                    p=p,
                    H=specified_pts_conf.p_time,
                    T=specified_pts_conf.q_time)

            # 文言の作成
            text = stringify_report_muzudho_recommends_points(
                    p=p,
                    number_of_series=number_of_series,
                    latest_theoretical_p=latest_theoretical_p,
                    specified_pts_conf=specified_pts_conf,    # TODO 任意のポイントを指定したい
                    presentable=presentable,
                    process=process,
                    turn_system=spec.turn_system)
                    
            print(text) # 表示

            with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ログファイルへ出力
            
            return


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
