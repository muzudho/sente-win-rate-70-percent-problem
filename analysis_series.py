#
# 分析
# python analysis_series.py
#
#   ［先後固定制］
#   表が出る確率（p）が偏ったコインを、指定回数投げる
#

import traceback
import random
import math

import pandas as pd

from library import HEAD, TAIL, ALICE, FACE_OF_COIN, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, ArgumentOfSequenceOfPlayout, ScoreBoard
from library.file_paths import get_analysis_series_log_file_path
from library.views import stringify_series_log, stringify_analysis_series


def analysis_series(spec, series_rule, trial_results_for_one_series, title):
    """［シリーズ］１つ分を分析します
    
    Parameters
    ----------
    spec : Specification
        ［仕様］
    series_rule : SeriesRule
        ［シリーズ・ルール］
    """

    score_board = ScoreBoard(
            spec=spec,
            series_rule=series_rule,
            list_of_face_of_coin=trial_results_for_one_series.list_of_face_of_coin)
    
    csv = score_board.stringify_csv()

    print(csv) # 表示

    # ログ出力
    with open(get_analysis_series_log_file_path(turn_system=turn_system), 'a', encoding='utf8') as f:
        f.write(f"{csv}\n")    # ファイルへ出力


    # # FIXME ［先後固定制］と［先後交互制］の処理を同じにしたい
    # if turn_system == WHEN_FROZEN_TURN:
    #     text = stringify_series_log(
    #             # ［表が出る確率］（指定値）
    #             p=spec.p,
    #             failure_rate=spec.failure_rate,
    #             # ［かくきんシステムのｐの構成］
    #             series_rule=series_rule,
    #             # ［シリーズ］１つ分の試行結果
    #             trial_results_for_one_series=trial_results_for_one_series,
    #             # タイトル
    #             title=title,
    #             turn_system=spec.turn_system)
    

    # print(text) # 表示

    # # ログ出力
    # with open(get_analysis_series_log_file_path(turn_system=turn_system), 'a', encoding='utf8') as f:
    #     f.write(f"{text}\n")    # ファイルへ出力


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        prompt = f"""\
What is the probability of flipping a coin and getting heads?
Example: 70% is 0.7
? """
        specified_p = float(input(prompt))


        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        prompt = f"""\
p_step?
Example: 2
? """
        specified_p_step = int(input(prompt))


        prompt = f"""\
q_step?
Example: 3
? """
        specified_q_step = int(input(prompt))


        prompt = f"""\
Span?
Example: 6
? """
        specified_span = int(input(prompt))


        prompt = f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """
        choice = input(prompt)

        if choice == '1':
            turn_system = WHEN_FROZEN_TURN

        elif choice == '2':
            turn_system = WHEN_ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        # 仕様
        spec = Specification(
                p=specified_p,
                failure_rate=specified_failure_rate,
                turn_system=turn_system)

        # ［シリーズ・ルール］。任意に指定します
        specified_series_rule = SeriesRule.make_series_rule_base(
                failure_rate=specified_failure_rate,
                p_step=specified_p_step,
                q_step=specified_q_step,
                span=specified_span,
                turn_system=turn_system)


        list_of_trial_results_for_one_series = []

        # FIXME 動作テスト
        list_of_all_pattern_face_of_coin = SequenceOfFaceOfCoin.make_list_of_all_pattern_face_of_coin(
                can_failure=False,
                series_rule=specified_series_rule)
        

        distinct_set = set()


        for list_of_face_of_coin in list_of_all_pattern_face_of_coin:
            #print(f"動作テスト {list_of_face_of_coin=}")

            #
            # 到達できない棋譜は除去しておきたい
            #

            #old_number_of_times = len(list_of_face_of_coin)

            # ［シリーズ］１つ分の試行結果を返す
            trial_results_for_one_series = judge_series(
                    spec=spec,
                    series_rule=specified_series_rule,
                    list_of_face_of_coin=list_of_face_of_coin)


            # FIXME 検証
            if trial_results_for_one_series.number_of_times < specified_series_rule.shortest_coins:
                text = f"{spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_times} が理論値 {specified_series_rule.shortest_coins} を下回った"
                print(f"""{text}
{list_of_face_of_coin=}
{specified_series_rule.longest_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
                raise ValueError(text)

            # FIXME 検証
            if specified_series_rule.longest_coins < trial_results_for_one_series.number_of_times:
                text = f"{spec.p=} 最長対局数の実際値 {trial_results_for_one_series.number_of_times} が理論値 {specified_series_rule.longest_coins} を上回った"
                print(f"""{text}
{list_of_face_of_coin=}
{specified_series_rule.shortest_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
                raise ValueError(text)



            # コインの出目のリストはサイズが切り詰められて縮まってるケースがある
            id = ''.join([str(num) for num in trial_results_for_one_series.list_of_face_of_coin])

            # 既に処理済みのものはスキップ
            if id in distinct_set:
                print(f"スキップ  {id=}  {trial_results_for_one_series.list_of_face_of_coin=}  {list_of_face_of_coin=}")
                continue

            distinct_set.add(id)


            # if trial_results_for_one_series.number_of_times < old_number_of_times:
            #     # 棋譜の長さが短くなったということは、到達できない記録が混ざっていたということです。
            #     #print(f"到達できない棋譜を除去 {trial_results_for_one_series.number_of_times=}  {old_number_of_times=}")
            #     pass

            # elif old_number_of_times < specified_series_rule.shortest_coins:
            #     # 棋譜の長さが足りていないということは、最後までプレイしていない
            #     #print(f"最後までプレイしていない棋譜を除去 {old_number_of_times=}  {specified_series_rule.shortest_coins=}")
            #     pass

            # #
            # # 引分け不可のときに、［最短対局数］までプレイして［目標の点数］へ足りていない棋譜が混ざっているなら、除去したい
            # #
            # elif specified_failure_rate == 0.0 and trial_results_for_one_series.is_no_won(opponent_pair=FACE_OF_COIN):
            #     #print(f"引分け不可のときに、［最短対局数］までプレイして［目標の点数］へ足りていない棋譜が混ざっているなら、除去 {specified_failure_rate=}")
            #     pass

            # else:

            list_of_trial_results_for_one_series.append(trial_results_for_one_series)

        # # 表示
        # print(stringify_analysis_series(
        #         spec=spec,
        #         list_of_trial_results_for_one_series=list_of_trial_results_for_one_series))

        for trial_results_for_one_series in list_of_trial_results_for_one_series:
            analysis_series(
                    spec=spec,
                    series_rule=specified_series_rule,
                    trial_results_for_one_series=trial_results_for_one_series,
                    title='（先後固定制）    むずでょセレクション')


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
