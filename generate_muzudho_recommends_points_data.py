#
# 生成
# python generate_muzudho_recommends_points_data.py
#
#   TODO むずでょが推奨する［かくきんシステムのｐの構成］一覧の各種 CSV を生成する。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import round_letro, calculate_probability
from file_paths import get_muzudho_recommends_points_csv_file_path
from database import get_df_even, get_df_muzudho_recommends_points, get_df_muzudho_recommends_points
from views import parse_process_element


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_muzudho_recommends_points.log'

OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


def generate_report(p, failure_rate, turn_system):
    if turn_system == WHEN_ALTERNATING_TURN:
        """［先後交互制］"""

        df_ev = get_df_even(turn_system=turn_system)
        df_mr = get_df_muzudho_recommends_points(turn_system=turn_system)

        for            p,          failure_rate,          best_p,          best_p_error,          best_number_of_series,          best_p_step,          best_q_step,          best_span,          latest_p,          latest_p_error,          latest_number_of_series,          latest_p_step,          latest_q_step,          latest_span,          process in\
            zip(df_ev['p'], df_ev['failure_rate'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_number_of_series'], df_ev['best_p_step'], df_ev['best_q_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_number_of_series'], df_ev['latest_p_step'], df_ev['latest_q_step'], df_ev['latest_span'], df_ev['process']):

            # ［計算過程］一覧
            #
            #   NOTE ［計算過程］リストの後ろの方のデータの方が精度が高い
            #   NOTE ［最長対局数］を気にする。長すぎるものは採用しづらい
            #
            process_list = process[1:-1].split('] [')

            #
            #   ［計算過程］が量が多くて調べものをしづらいので、量を減らします。
            #   NOTE ［最小対局数］と［最長対局数］が同じデータもいっぱいあります。その場合、リストの最初に出てきたもの以外は捨てます
            #
            process_element_dict = dict()

            for process_element in process_list:
                p_error, head, tail, span, shortest, longest = parse_process_element(process_element)

                if p_error is not None:
                    key = (shortest, longest)
                    value = (p_error, head, tail, span, shortest, longest)
                    if key not in process_element_dict:
                        process_element_dict[key] = value

            comment_element_list = []
            for key, value in process_element_dict.items():
                p_error, head, tail, span, shortest, longest = value
                comment_element_list.append(f'[{p_error*100+50:.4f} ％（{p_error*100:+.4f}） {head}表 {tail}裏 {span}目 {shortest}～{longest}局]')

            # ［計算過程］列を更新
            df_mr.loc[df_mr['p']==p, ['process']] = ' '.join(comment_element_list)

            # CSV保存
            df_mr.to_csv(get_muzudho_recommends_points_csv_file_path(turn_system=turn_system),
                    # ［計算過程］列は長くなるので末尾に置きたい
                    columns=['p', 'number_of_series', 'p_step', 'q_step', 'span', 'presentable', 'comment', 'process'],
                    index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた

        return


    if turn_system == WHEN_FROZEN_TURN:
        """［先後固定制］"""

        df_ev = get_df_even(turn_system=turn_system)
        df_mr = get_df_muzudho_recommends_points(turn_system=turn_system)

        for            p,          failure_rate,          best_p,          best_p_error,          best_number_of_series,          best_p_step,          best_q_step,          best_span,          latest_p,          latest_p_error,          latest_number_of_series,          latest_p_step,          latest_q_step,          latest_span,          process in\
            zip(df_ev['p'], df_ev['failure_rate'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_number_of_series'], df_ev['best_p_step'], df_ev['best_q_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_number_of_series'], df_ev['latest_p_step'], df_ev['latest_q_step'], df_ev['latest_span'], df_ev['process']):

            # ［計算過程］一覧
            #
            #   NOTE ［計算過程］リストの後ろの方のデータの方が精度が高い
            #   NOTE ［最長対局数］を気にする。長すぎるものは採用しづらい
            #
            process_list = process[1:-1].split('] [')

            #
            #   ［計算過程］が量が多くて調べものをしづらいので、量を減らします。
            #   NOTE ［最小対局数］と［最長対局数］が同じデータもいっぱいあります。その場合、リストの最初に出てきたもの以外は捨てます
            #
            process_element_dict = dict()

            for process_element in process_list:
                p_error, head, tail, span, shortest, longest = parse_process_element(process_element)

                if p_error is not None:
                    key = (shortest, longest)
                    value = (p_error, head, tail, span, shortest, longest)
                    if key not in process_element_dict:
                        process_element_dict[key] = value

            comment_element_list = []
            for key, value in process_element_dict.items():
                p_error, head, tail, span, shortest, longest = value
                comment_element_list.append(f'[{p_error*100+50:.4f} ％（{p_error*100:+.4f}） {head}表 {tail}裏 {span}目 {shortest}～{longest}局]')

            # ［計算過程］列を更新
            df_mr.loc[df_mr['p']==p, ['process']] = ' '.join(comment_element_list)

            # CSV保存
            df_mr.to_csv(get_muzudho_recommends_points_csv_file_path(turn_system=turn_system),
                    # ［計算過程］列は長くなるので末尾に置きたい
                    columns=['p', 'p_step', 'q_step', 'span', 'presentable', 'comment', 'process'],
                    index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた
            
            return


    raise ValueError(f"{turn_system=}")


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        print(f"""\
What is the probability of flipping a coin and getting heads?
Example: 70% is 0.7
? """)
        p = float(input())


        print(f"""\
What is the failure rate?
Example: 10% is 0.1
? """)
        failure_rate = float(input())


        # ［先後交互制］
        generate_report(p=p, failure_rate=failure_rate, turn_system=WHEN_ALTERNATING_TURN)

        # ［先後固定制］
        generate_report(p=p, failure_rate=failure_rate, turn_system=WHEN_FROZEN_TURN)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
