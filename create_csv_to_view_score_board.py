#
# 分析
# python create_csv_to_view_score_board.py
#
#   １シリーズのコインの出目について、全パターン網羅した表を作成します
#

import traceback
import random
import math

import pandas as pd

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FACE_OF_COIN, FROZEN_TURN, ALTERNATING_TURN, Specification, SeriesRule, judge_series, Converter, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, ScoreBoard
from library.file_paths import get_score_board_log_file_path, get_score_board_csv_file_path
from library.views import stringify_series_log, stringify_csv_of_score_board


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
    
    csv = stringify_csv_of_score_board(scoreboard=score_board)

    print(csv) # 表示

    # CSVファイル出力
    csv_file_path = get_score_board_csv_file_path(
            p=spec.p,
            failure_rate=spec.failure_rate,
            turn_system=turn_system,
            h_step=series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
            t_step=series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL),
            span=series_rule.step_table.span)
    print(f"write csv to `{csv_file_path}` file ...")
    with open(csv_file_path, 'a', encoding='utf8') as f:
        f.write(f"{csv}\n")


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の先手勝率］
        prompt = f"""\
What is the probability of flipping a coin and getting heads?
Example: 70% is 0.7
? """
        specified_p = float(input(prompt))


        # ［将棋の引分け率］
        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］
        prompt = f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """
        choice = input(prompt)

        if choice == '1':
            turn_system = FROZEN_TURN

        elif choice == '2':
            turn_system = ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        # ［先手で勝ったときの勝ち点］
        prompt = f"""\
h_step?
Example: 2
? """
        specified_h_step = int(input(prompt))


        # ［後手で勝ったときの勝ち点］
        prompt = f"""\
t_step?
Example: 3
? """
        specified_t_step = int(input(prompt))


        # ［目標の点数］
        prompt = f"""\
Span?
Example: 6
? """
        specified_span = int(input(prompt))


        # CSVファイル出力（上書き）
        #
        #   ファイルをクリアーしたいだけ
        #
        csv_file_path = get_score_board_csv_file_path(
                p=specified_p,
                failure_rate=specified_failure_rate,
                turn_system=turn_system,
                h_step=specified_h_step,
                t_step=specified_t_step,
                span=specified_span)
        print(f"write csv to `{csv_file_path}` file ...")
        with open(csv_file_path, 'w', encoding='utf8') as f:
            f.write(f"""\
スコアボード

""")


        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trials_series = 1


        # 仕様
        spec = Specification(
                p=specified_p,
                failure_rate=specified_failure_rate,
                turn_system=turn_system)

        # ［シリーズ・ルール］。任意に指定します
        specified_series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                trials_series=specified_trials_series,      # この［シリーズ・ルール］を作成するために行われた［試行シリーズ数］
                h_step=specified_h_step,
                t_step=specified_t_step,
                span=specified_span)


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

            #old_number_of_coins = len(list_of_face_of_coin)

            # 最短対局数を下回る対局シートはスキップします
            if len(list_of_face_of_coin) < specified_series_rule.shortest_coins:
                #print(f"{spec.p=} 指定の対局シートの長さ {len(list_of_face_of_coin)} は、最短対局数の理論値 {specified_series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません")
                continue

            # ［シリーズ］１つ分の試行結果を返す
            trial_results_for_one_series = judge_series(
                    spec=spec,
                    series_rule=specified_series_rule,
                    list_of_face_of_coin=list_of_face_of_coin)


            # FIXME 検証
            if trial_results_for_one_series.number_of_coins < specified_series_rule.shortest_coins:
                text = f"{spec.p=} 最短対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {specified_series_rule.shortest_coins} を下回った"
                print(f"""{text}
{list_of_face_of_coin=}
{specified_series_rule.upper_limit_coins=}
{trial_results_for_one_series.stringify_dump('   ')}
""")
                raise ValueError(text)

            # FIXME 検証
            if specified_series_rule.upper_limit_coins < trial_results_for_one_series.number_of_coins:
                text = f"{spec.p=} 上限対局数の実際値 {trial_results_for_one_series.number_of_coins} が理論値 {specified_series_rule.upper_limit_coins} を上回った"
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

            list_of_trial_results_for_one_series.append(trial_results_for_one_series)


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
