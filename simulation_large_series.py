#
# シミュレーション
# python simulation_large_series.py
#
#   ［コインの表が出る確率］ p=0.50 ～ 0.99 までのデータを一覧する
#

import traceback

from library import WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, round_letro, Specification, SeriesRule, judge_series, LargeSeriesTrialSummary, ElementaryEventSequence, SequenceOfFaceOfCoin, ArgumentOfSequenceOfPlayout
from library.file_paths import get_simulation_large_series_log_file_path
from library.database import get_df_muzudho_recommends_points
from library.views import stringify_simulation_log


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        print(f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """)

        choice = input()

        if choice == '1':
            turn_system = WHEN_FROZEN_TURN

        elif choice == '2':
            turn_system = WHEN_ALTERNATING_TURN

        else:
            raise ValueError(f"{choice=}")


        print(f"""\
What is the failure rate?
Example: 10% is 0.1
? """)
        failure_rate = float(input())


        print(f"""\
How many times do you want to try the series?
Example: 2000000
? """)
        number_of_series = int(input())


        title='むずでょセレクション'


        df_mrp = get_df_muzudho_recommends_points(turn_system=turn_system)

        for             p,           failure_rate,           p_step,           q_step,           span,           presentable,           comment,           process in\
            zip(df_mrp['p'], df_mrp['failure_rate'], df_mrp['p_step'], df_mrp['q_step'], df_mrp['span'], df_mrp['presentable'], df_mrp['comment'], df_mrp['process']):

            # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
            p_step = round_letro(p_step)
            q_step = round_letro(q_step)
            span = round_letro(span)

            if p_step < 1:
                print(f"データベースの値がおかしいのでスキップ  {p=}  {failure_rate=}  {p_step=}")
                continue


            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=failure_rate,
                    turn_system=turn_system)

            # ［シリーズ・ルール］。任意に指定します
            series_rule = SeriesRule.make_series_rule_base(
                    failure_rate=spec.failure_rate,
                    p_step=p_step,
                    q_step=q_step,
                    span=span,
                    turn_system=turn_system)

            series_result_list = []

            # ［最長対局数］は計算で求められます
            shortest_times = series_rule.number_of_shortest_time()
            number_of_longest_time = series_rule.number_of_longest_time()
            if number_of_longest_time < shortest_times:
                text = f"［最短対局数］{shortest_times} が、［最長対局数］{number_of_longest_time} より長いです"
                print(f"""\
{text}
spec:
{spec.stringify_dump('    ')}
{p_step=}
{q_step=}
{span=}
series_rule:
{series_rule.stringify_dump('   ')}
""")
                raise ValueError(text)

            for round in range(0, number_of_series):

                # 引数作成
                argument_of_sequence_of_playout = ArgumentOfSequenceOfPlayout(
                        p=p,
                        failure_rate=spec.failure_rate,
                        number_of_longest_time=number_of_longest_time)

                # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
                list_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                        argument_of_sequence_of_playout=argument_of_sequence_of_playout)

                # シリーズの結果を返す
                series_result = judge_series(
                        argument_of_sequence_of_playout=argument_of_sequence_of_playout,
                        list_of_face_of_coin=list_of_face_of_coin,
                        series_rule=series_rule,
                        turn_system=turn_system)
                #print(f"{series_result.stringify_dump()}")



                
                if series_result.number_of_times < series_rule.number_of_shortest_time():
                    text = f"{spec.p=} 最短対局数の実際値 {series_result.number_of_times} が理論値 {series_rule.number_of_shortest_time()} を下回った"
                    print(f"""{text}
{number_of_longest_time=}
{series_result.stringify_dump('   ')}
""")
                    raise ValueError(text)

                if series_rule.number_of_longest_time() < series_result.number_of_times:
                    text = f"{spec.p=} 最長対局数の実際値 {series_result.number_of_times} が理論値 {series_rule.number_of_longest_time()} を上回った"
                    print(f"""{text}
{number_of_longest_time=}
{series_result.stringify_dump('   ')}
""")
                    raise ValueError(text)



                series_result_list.append(series_result)


            # シミュレーションの結果
            large_series_trial_summary = LargeSeriesTrialSummary(
                    series_result_list=series_result_list)


            text = stringify_simulation_log(
                    # ［表が出る確率］（指定値）
                    p=spec.p,
                    # ［表も裏も出ない率］
                    failure_rate=spec.failure_rate,
                    # ［先後運用制度］
                    turn_system=turn_system,
                    # ［かくきんシステムのｐの構成］
                    series_rule=series_rule,
                    # シミュレーションの結果
                    large_series_trial_summary=large_series_trial_summary,
                    # タイトル
                    title=title)


            print(text) # 表示


            # ログ出力
            with open(get_simulation_large_series_log_file_path(
                    failure_rate=spec.failure_rate,
                    turn_system=turn_system), 'a', encoding='utf8') as f:
                f.write(f"{text}\n")    # ファイルへ出力


            # 表示とログ出力を終えた後でテスト
            if large_series_trial_summary.shortest_time_th < series_rule.number_of_shortest_time():
                raise ValueError(f"{spec.p=} 最短対局数の実際値 {large_series_trial_summary.shortest_time_th} が理論値 {series_rule.number_of_shortest_time()} を下回った")

            if series_rule.number_of_longest_time() < large_series_trial_summary.longest_time_th:
                raise ValueError(f"{spec.p=} 最長対局数の実際値 {large_series_trial_summary.longest_time_th} が理論値 {series_rule.number_of_longest_time()} を上回った")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
