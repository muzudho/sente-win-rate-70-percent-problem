#
# 生成
# python generate_even_series_rule.py
#
#   TODO 実際値ではなく、理論値を記録したい。 alternating_turn の方がそれに対応してない
#
#   ［表勝ちだけでの対局数］と、［裏勝ちだけでの対局数］を探索する。
#

import traceback
import random
import math
import time
import datetime
import pandas as pd

from library import HEAD, TAIL, ALICE, SUCCESSFUL, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, make_generation_algorythm, round_letro, ElementaryEventSequence, judge_series, SeriesRule, calculate_probability, LargeSeriesTrialSummary, Specification, SequenceOfFaceOfCoin, ArgumentOfSequenceOfPlayout, Candidate
from library.file_paths import get_even_series_rule_csv_file_path
from library.database import append_default_record_to_df_even, get_df_even, get_df_p, df_even_to_csv
from library.views import print_even_series_rule


# 勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
ABS_OUT_OF_ERROR = 0.51

# 十分小さいエラー
ABS_SMALL_ERROR = 0.00009

# 探索の上限
LIMIT_SPAN = 1001

# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 60

# CSV保存用タイマー
start_time_for_save = None
is_dirty_csv = False


def update_dataframe(df, p, failure_rate,
        best_p, best_p_error, best_number_of_series, best_series_rule,
        latest_p, latest_p_error, latest_number_of_series, latest_series_rule, candidates,
        turn_system):
    """データフレーム更新"""

    global start_time_for_save, is_dirty_csv

    # # 表示
    # print_even_series_rule(
    #         p=p,
    #         best_p=best_p,
    #         best_p_error=best_p_error,
    #         best_number_of_series=best_number_of_series,
    #         series_rule=best_series_rule)

    # ［調整後の表が出る確率］列を更新
    df.loc[df['p']==p, ['best_p']] = best_p
    df.loc[df['p']==p, ['latest_p']] = latest_p

    # ［調整後の表が出る確率の５割との誤差］列を更新
    df.loc[df['p']==p, ['best_p_error']] = best_p_error
    df.loc[df['p']==p, ['latest_p_error']] = latest_p_error

    # ［試行回数］列を更新
    df.loc[df['p']==p, ['best_number_of_series']] = best_number_of_series
    df.loc[df['p']==p, ['latest_number_of_series']] = latest_number_of_series

    # ［表勝ち１つの点数］列を更新
    df.loc[df['p']==p, ['best_p_step']] = best_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)
    df.loc[df['p']==p, ['latest_p_step']] = latest_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)

    # ［裏勝ち１つの点数］列を更新
    df.loc[df['p']==p, ['best_q_step']] = best_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)
    df.loc[df['p']==p, ['latest_q_step']] = latest_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)

    # ［目標の点数］列を更新 
    df.loc[df['p']==p, ['best_span']] = best_series_rule.step_table.span
    df.loc[df['p']==p, ['latest_span']] = latest_series_rule.step_table.span

    # ［シリーズ・ルール候補］列を更新
    df.loc[df['p']==p, ['candidates']] = candidates

    is_dirty_csv = True


def ready_records(df, specified_failure_rate, turn_system, generation_algorythm):
    """EVENテーブルについて、まず、行の存在チェック。無ければ追加"""
    is_append_new_record = False

    df_p = get_df_p()

    # ［コインを投げて表が出る確率］
    for p in df_p['p']:
        # 存在しなければデフォルトのレコード追加
        if not ((df['p'] == p) & (df['failure_rate'] == specified_failure_rate)).any():
            append_default_record_to_df_even(
                    df=df,
                    p=p,
                    failure_rate=specified_failure_rate)
            is_append_new_record = True

    if is_append_new_record:
        # CSV保存
        df_even_to_csv(df=df, turn_system=turn_system, generation_algorythm=generation_algorythm)


def iteration_deeping(df, abs_limit_of_error, specified_failure_rate, specified_number_of_series, turn_system, generation_algorythm):
    """反復深化探索の１セット

    Parameters
    ----------
    df : DataFrame
        データフレーム
    abs_limit_of_error : float
        リミット
    """

    global start_time_for_save, is_dirty_csv


    # まず、行の存在チェック。無ければ追加
    ready_records(df=df, specified_failure_rate=specified_failure_rate, turn_system=turn_system, generation_algorythm=generation_algorythm)


    for         p,       failure_rate,       best_p,       best_p_error,       best_number_of_series,       best_p_step,       best_q_step,       best_span,       latest_p,       latest_p_error,       latest_number_of_series,       latest_p_step,       latest_q_step,       latest_span,       candidates in\
        zip(df['p'], df['failure_rate'], df['best_p'], df['best_p_error'], df['best_number_of_series'], df['best_p_step'], df['best_q_step'], df['best_span'], df['latest_p'], df['latest_p_error'], df['latest_number_of_series'], df['latest_p_step'], df['latest_q_step'], df['latest_span'], df['candidates']):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_number_of_series = round_letro(best_number_of_series)
        best_p_step = round_letro(best_p_step)
        best_q_step = round_letro(best_q_step)
        best_span = round_letro(best_span)
        latest_p_step = round_letro(latest_p_step)
        latest_q_step = round_letro(latest_q_step)
        latest_span = round_letro(latest_span)


        # 該当行以外は無視
        if specified_failure_rate != failure_rate:
            continue


        best_series_rule = SeriesRule.make_series_rule_base(
                failure_rate=failure_rate,
                p_step=best_p_step,
                q_step=best_q_step,
                span=best_span,
                turn_system=turn_system)

        update_count = 0
        passage_count = 0
        is_cutoff = False
        is_good = False

        # 既存データの方が信用のおけるデータだった場合、スキップ
        # エラーが十分小さければスキップ
        if specified_number_of_series < best_number_of_series or abs(best_p_error) <= ABS_SMALL_ERROR:
            is_automatic = False
            # FIXME 全部のレコードがスキップされたとき、無限ループに陥る

        # アルゴリズムで求めるケース
        else:
            #print(f"[p={p}]", end='', flush=True)
            is_automatic = True

            # 仕様
            spec = Specification(
                    p=p,
                    failure_rate=failure_rate,
                    turn_system=turn_system)

            #
            # ［目標の点数］、［裏勝ち１つの点数］、［表勝ち１つの点数］を１つずつ進めていく探索です。
            #
            # ［目標の点数］＞＝［裏勝ち１つの点数］＞＝［表勝ち１つの点数］という関係があります。
            #
            start_q_step = latest_q_step
            start_p_step = latest_p_step + 1      # 終わっているところの次から始める      NOTE p_step の初期値は 0 であること
            for cur_span in range(latest_span, LIMIT_SPAN):
                for cur_q_step in range(start_q_step, cur_span + 1):
                    for cur_p_step in range(start_p_step, cur_q_step + 1):

                        # ［シリーズ・ルール］
                        latest_series_rule = SeriesRule.make_series_rule_base(
                                failure_rate=failure_rate,
                                p_step=cur_p_step,
                                q_step=cur_q_step,
                                span=cur_span,
                                turn_system=spec.turn_system)


                        # 力任せ探索の場合                        
                        if generation_algorythm == BRUTE_FORCE:
                            series_result_list = []

                            for i in range(0, specified_number_of_series):

                                # 引数作成
                                argument_of_sequence_of_playout = ArgumentOfSequenceOfPlayout(
                                        p=p,
                                        failure_rate=failure_rate,
                                        number_of_longest_time=latest_series_rule.number_of_longest_time)

                                # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
                                list_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                                        argument_of_sequence_of_playout=argument_of_sequence_of_playout)

                                # 疑似のリストをもとに、シリーズとして見てみる
                                trial_results_for_one_series = judge_series(
                                        argument_of_sequence_of_playout=argument_of_sequence_of_playout,
                                        list_of_face_of_coin=list_of_face_of_coin,
                                        series_rule=latest_series_rule)
                                
                                series_result_list.append(trial_results_for_one_series)
                            
                            # シミュレーションの結果
                            large_series_trial_summary = LargeSeriesTrialSummary(
                                    series_result_list=series_result_list)

                            # Ａさんが勝った回数
                            latest_p = large_series_trial_summary.number_of_wins(winner=ALICE) / specified_number_of_series
                            latest_p_error = latest_p - 0.5


                        # 理論値の場合
                        elif generation_algorythm == THEORETICAL:
                            latest_p = calculate_probability(
                                    p=p,
                                    H=latest_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                                    T=latest_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))
                            latest_p_error = latest_p - 0.5


                        else:
                            raise ValueError(f"{generation_algorythm=}")


                        if abs(latest_p_error) < abs(best_p_error):
                            update_count += 1
                            best_p = latest_p
                            best_p_error = latest_p_error
                            best_series_rule = latest_series_rule

                            # ［最短対局数］［最長対局数］
                            shortest_time = best_series_rule.number_of_shortest_time
                            longest_time = best_series_rule.number_of_longest_time

                            # ［シリーズ・ルール候補］
                            candidate_obj = Candidate(
                                    p_error=best_p_error,
                                    number_of_series=best_number_of_series,
                                    p_step=best_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                                    q_step=best_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL),
                                    span=best_series_rule.step_table.span,
                                    number_of_shortest_time=shortest_time,
                                    number_of_longest_time=longest_time)
                            candidate_str = candidate_obj.as_str()
                            print(f"[p={p*100:2.0f} ％  failure_rate={specified_failure_rate*100:2.0f} ％] {candidate_str}", flush=True) # すぐ表示

                            # ［シリーズ・ルール候補］列を更新
                            #
                            #   途中の計算式。半角空裏区切り
                            #
                            if isinstance(candidates, str):
                                candidates = f"{candidates} {candidate_str}"
                            else:
                                candidates = candidate_str

                            # 表示とデータフレーム更新
                            update_dataframe(
                                    df=df,
                                    p=p,
                                    failure_rate=failure_rate,
                                    best_p=best_p,
                                    best_p_error=best_p_error,
                                    best_number_of_series=specified_number_of_series,
                                    best_series_rule=best_series_rule,
                                    latest_p=latest_p,
                                    latest_p_error=latest_p_error,
                                    latest_number_of_series=specified_number_of_series,
                                    latest_series_rule=latest_series_rule,
                                    candidates=candidates,
                                    turn_system=spec.turn_system)

                            # 指定間隔（秒）で保存
                            end_time_for_save = time.time()
                            if is_dirty_csv and INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                                start_time_for_save = end_time_for_save
                                is_dirty_csv = False

                                # CSV保存
                                print(f"[{datetime.datetime.now()}] CSV保存 ...")
                                df_even_to_csv(df=df, turn_system=turn_system, generation_algorythm=generation_algorythm)


                            # 十分な答えが出たか、複数回の更新があったとき、探索を打ち切ります
                            if abs(best_p_error) < abs_limit_of_error or 2 < update_count:
                                is_good = True
                                is_cutoff = True
                                # # 進捗バー
                                # print('cutoff (good)', flush=True)
                                break

                        else:
                            passage_count += 1
                            latest_candidates = candidates

                            # # 進捗バー
                            # print('.', end='', flush=True)

                            # 空振りが多いとき、探索を打ち切ります
                            if 30 < passage_count:
                                is_cutoff = True
                                # # 進捗バー
                                # print('cutoff (procrastinate)', flush=True)
                                break

                    start_p_step = 1

                    if is_cutoff:
                        break

                start_q_step = 1

                if is_cutoff:
                    break

            # print() # 改行


        if is_good:
            continue


        # 空振りが１回でもあれば、途中状態を保存
        if 0 < passage_count:
            # 表示とデータフレーム更新
            update_dataframe(
                    df=df,
                    p=p,
                    failure_rate=failure_rate,
                    best_p=best_p,
                    best_p_error=best_p_error,
                    best_number_of_series=specified_number_of_series,
                    best_series_rule=best_series_rule,
                    latest_p=latest_p,
                    latest_p_error=latest_p_error,
                    latest_number_of_series=specified_number_of_series,
                    latest_series_rule=latest_series_rule,
                    candidates=latest_candidates,
                    turn_system=turn_system)

            # 指定間隔（秒）で保存
            end_time_for_save = time.time()
            if is_dirty_csv and INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                start_time_for_save = end_time_for_save
                is_dirty_csv = False

                # CSV保存
                print(f"[{datetime.datetime.now()}] CSV保存 ...")
                df_even_to_csv(df=df, turn_system=turn_system, generation_algorythm=generation_algorythm)


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
#         print(f"""\
# What is the probability of flipping a coin and getting heads?
# Example: 70% is 0.7
# ? """)
#         p = float(input())


        # ［先後が回ってくる制度］を尋ねる
        print(f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """)
        choice = input()
        if choice == '1':
            specified_turn_system = WHEN_FROZEN_TURN
        elif choice == '2':
            specified_turn_system = WHEN_ALTERNATING_TURN
        else:
            raise ValueError(f"{choice=}")


        print(f"""\
What is the failure rate?
Example: 10% is 0.1
? """)
        specified_failure_rate = float(input())


        # ［試行シリーズ回数］を尋ねる
        print(f"""\
How many times do you want to try the series?
Example: 2000000
? """)
        specified_number_of_series = int(input())




        generation_algorythm = make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
        if generation_algorythm == BRUTE_FORCE:
            print("力任せ探索を行います")
        elif generation_algorythm == THEORETICAL:
            print("理論値を求めます")
        else:
            raise ValueError(f"{generation_algorythm=}")


        df_ev = get_df_even(turn_system=specified_turn_system, generation_algorythm=generation_algorythm)
        #print(df_ev)


        start_time_for_save = time.time()
        is_dirty_csv = False


        # 反復深化探索
        # ===========
        #
        #   ［エラー］が 0 になることを目指していますが、最初から 0 を目指すと、もしかするとエラーは 0 にならなくて、
        #   処理が永遠に終わらないかもしれません。
        #   そこで、［エラー］列は、一気に 0 を目指すのではなく、手前の目標を設定し、その目標を徐々に小さくしていきます。
        #   リミットを指定して、リミットより［エラー］が下回ったら、処理を打ち切ることにします
        #
        abs_limit_of_error = ABS_OUT_OF_ERROR

        while ABS_SMALL_ERROR < abs_limit_of_error:
            # ［エラー］列で一番大きい値を取得します
            #
            #   ［調整後の表が出る確率］を 0.5 になるように目指します。［エラー］列は、［調整後の表が出る確率］と 0.5 の差の絶対値です
            #
            worst_abs_best_p_error = max(abs(df_ev['best_p_error'].min()), abs(df_ev['best_p_error'].max()))
            # print(f"{worst_abs_best_p_error=}")

            # とりあえず、［調整後の表が出る確率］が［最大エラー］値の半分未満になるよう目指す
            #
            #   NOTE P=0.99 の探索は、 p=0.50～0.98 を全部合わせた処理時間よりも、時間がかかるかも。だから p=0.99 のケースだけに合わせて時間調整するといいかも。
            #   NOTE エラー値を下げるときに、８本勝負の次に９本勝負を見つけられればいいですが、そういうのがなく次が１５本勝負だったりするような、跳ねるケースでは処理が長くなりがちです。リミットをゆっくり下げればいいですが、どれだけ気を使っても避けようがありません
            #
            # 半分、半分でも速そうなので、１０分の９を繰り返す感じで。
            abs_limit_of_error = worst_abs_best_p_error * 9 / 10

            iteration_deeping(
                    df_ev,
                    abs_limit_of_error,
                    specified_failure_rate=specified_failure_rate,
                    specified_number_of_series=specified_number_of_series,
                    turn_system=specified_turn_system,
                    generation_algorythm=generation_algorythm)


        if is_dirty_csv:
            is_dirty_csv = False

            # 最後に CSV保存
            print(f"[{datetime.datetime.now()}] 最後に CSV保存 ...")
            df_even_to_csv(df=df_ev, turn_system=specified_turn_system, generation_algorythm=generation_algorythm)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
