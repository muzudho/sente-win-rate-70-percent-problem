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

from library import round_letro, calculate_probability, PointsConfiguration
from database import get_df_muzudho_recommends_points, get_df_muzudho_recommends_points
from views import stringify_report_muzudho_recommends_points_ft, stringify_report_muzudho_recommends_points_at


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_muzudho_recommends_points.log'

CSV_FILE_PATH_MR_FT = './data/muzudho_recommends_points_when_frozen_turn.csv'
CSV_FILE_PATH_MR_AT = './data/muzudho_recommends_points_when_alternating_turn.csv'


FAILURE_RATE = 0.0


OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


def generate_report(turn_system):
    if turn_system == WHEN_ALTERNATING_TURN:
        """［先後交互制］"""

        df_mr_at = get_df_muzudho_recommends_points(turn_system=WHEN_ALTERNATING_TURN)

        for               p,             number_of_series,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_at['p'], df_mr_at['number_of_series'], df_mr_at['b_step'], df_mr_at['w_step'], df_mr_at['span'], df_mr_at['presentable'], df_mr_at['comment'], df_mr_at['process']):

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            # NOTE ［先後交代制］では、理論値の出し方が分からないので、理論値ではなく、実際値をコメントから拾って出力する
            latest_theoretical_p = calculate_probability(
                    p=p,
                    H=specified_points_configuration.b_time,
                    T=specified_points_configuration.w_time)

            # 文言の作成
            text = stringify_report_muzudho_recommends_points_at(
                    p=p,
                    number_of_series=number_of_series,
                    latest_theoretical_p=latest_theoretical_p,
                    specified_points_configuration=specified_points_configuration,    # TODO 任意のポイントを指定したい
                    presentable=presentable,
                    process=process)
            print(text) # 表示

            with open(REPORT_FILE_PATH, 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ログファイルへ出力

        return

    if turn_system == WHEN_FROZEN_TURN:
        """［先後固定制］"""

        df_mr_ft = get_df_muzudho_recommends_points(turn_system=WHEN_FROZEN_TURN)

        for               p,             b_step,             w_step,             span,             presentable,             comment,             process in\
            zip(df_mr_ft['p'], df_mr_ft['b_step'], df_mr_ft['w_step'], df_mr_ft['span'], df_mr_ft['presentable'], df_mr_ft['comment'], df_mr_ft['process']):

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=FAILURE_RATE,
                    turn_system=WHEN_ALTERNATING_TURN)

            # ［かくきんシステムのｐの構成］。任意に指定します
            specified_points_configuration = PointsConfiguration(
                    failure_rate=FAILURE_RATE,
                    b_step=b_step,
                    w_step=w_step,
                    span=span)

            # NOTE 実際値ではなく、理論値を出力する
            latest_theoretical_p = calculate_probability(
                    p=p,
                    H=specified_points_configuration.b_time,
                    T=specified_points_configuration.w_time)

            # 文言の作成
            text = stringify_report_muzudho_recommends_points_ft(
                    p=p,
                    latest_theoretical_p=latest_theoretical_p,
                    specified_points_configuration=specified_points_configuration,    # TODO 任意のポイントを指定したい
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

        raise
