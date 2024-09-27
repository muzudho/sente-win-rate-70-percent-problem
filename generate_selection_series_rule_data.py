#
# 生成
# python generate_selection_series_rule_data.py
#
#   TODO むずでょが推奨する［かくきんシステムのｐの構成］一覧の各種 CSV を生成する。
#

import traceback
import datetime
import random
import math
import pandas as pd

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, make_generation_algorythm, round_letro, calculate_probability, Candidate
from library.file_paths import get_selection_series_rule_csv_file_path
from library.database import get_df_even, get_df_selection_series_rule, df_ssr_to_csv, get_df_p, append_default_record_to_df_ssr


# とりあえず、ログファイルとして出力する。あとで手動で拡張子を .txt に変えるなどしてください
REPORT_FILE_PATH = 'reports/report_selection_series_rule.log'

OUT_OF_ERROR = 0.51

# 先手勝率が 5割 +-0.03未満なら良い
LIMIT_ERROR = 0.03


def ready_records(df, specified_failure_rate, turn_system):
    """MRPテーブルについて、まず、行の存在チェック。無ければ追加"""
    is_append_new_record = False

    df_p = get_df_p()

    # ［コインを投げて表が出る確率］
    for p in df_p['p']:
        # 存在しなければデフォルトのレコード追加
        if not ((df['p'] == p) & (df['failure_rate'] == specified_failure_rate)).any():
            append_default_record_to_df_ssr(
                    df=df,
                    p=p,
                    failure_rate=specified_failure_rate)
            is_append_new_record = True

    if is_append_new_record:
        # CSV保存
        df_ssr_to_csv(df=df, turn_system=turn_system)


def generate_data(specified_failure_rate, turn_system, generation_algorythm):

    df_ev = get_df_even(turn_system=turn_system, generation_algorythm=generation_algorythm)
    df_ssr = get_df_selection_series_rule(turn_system=turn_system)

    # まず、行の存在チェック。無ければ追加
    ready_records(df=df_ssr, specified_failure_rate=specified_failure_rate, turn_system=turn_system)


    for            p,          failure_rate,          best_p,          best_p_error,          best_number_of_series,          best_p_step,          best_q_step,          best_span,          latest_p,          latest_p_error,          latest_number_of_series,          latest_p_step,          latest_q_step,          latest_span,          candidates in\
        zip(df_ev['p'], df_ev['failure_rate'], df_ev['best_p'], df_ev['best_p_error'], df_ev['best_number_of_series'], df_ev['best_p_step'], df_ev['best_q_step'], df_ev['best_span'], df_ev['latest_p'], df_ev['latest_p_error'], df_ev['latest_number_of_series'], df_ev['latest_p_step'], df_ev['latest_q_step'], df_ev['latest_span'], df_ev['candidates']):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_p_step = round_letro(best_p_step)
        best_q_step = round_letro(best_q_step)
        best_span = round_letro(best_span)
        latest_p_step = round_letro(latest_p_step)
        latest_q_step = round_letro(latest_q_step)
        latest_span = round_letro(latest_span)


        # ［計算過程］一覧
        #
        #   NOTE ［計算過程］リストの後ろの方のデータの方が精度が高い
        #   NOTE ［最長対局数］を気にする。長すぎるものは採用しづらい
        #
        if isinstance(candidate, float):  # nan が入ってる？
            candidate_list = []
        else:
            candidate_list = candidate[1:-1].split('] [')


        #
        #   ［計算過程］が量が多くて調べものをしづらいので、量を減らします。
        #   NOTE ［最小対局数］と［最長対局数］が同じデータもいっぱいあります。その場合、リストの最初に出てきたもの以外は捨てます
        #
        candidate_element_dict = dict()


        for candidate_element in candidate_list:
            candidate_obj = Candidate.parse_candidate(candidate_element)

            if candidate_obj.p_error is not None:
                key = (candidate_obj.number_of_shortest_time, candidate_obj.number_of_longest_time)
                if key not in candidate_element_dict:
                    candidate_element_dict[key] = candidate_obj


        comment_element_list = []
        for key, candidate_obj in candidate_element_dict.items():
            comment_element_list.append(candidate_obj.as_str())


        # ［計算過程］列を更新
        df_ssr.loc[df_ssr['p']==p, ['candidates']] = ' '.join(comment_element_list)


        # CSV保存
        df_ssr_to_csv(df=df_ssr, turn_system=turn_system)


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
#         prompt = f"""\
# What is the probability of flipping a coin and getting heads?
# Example: 70% is 0.7
# ? """
#         p = float(input(prompt))


        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))



        # ［先後固定制］
        generation_algorythm_ft = make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=WHEN_FROZEN_TURN)
        generate_data(specified_failure_rate=specified_failure_rate, turn_system=WHEN_FROZEN_TURN, generation_algorythm=generation_algorythm_ft)

        # ［先後交互制］
        generation_algorythm_at = make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=WHEN_ALTERNATING_TURN)
        generate_data(specified_failure_rate=specified_failure_rate, turn_system=WHEN_ALTERNATING_TURN, generation_algorythm=generation_algorythm_at)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())