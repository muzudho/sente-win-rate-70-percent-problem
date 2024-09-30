#
# 生成
# python create_a_csv_to_data_evenizer.py
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

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, ABS_OUT_OF_ERROR, Converter, round_letro, judge_series, SeriesRule, calculate_probability, LargeSeriesTrialSummary, Specification, SequenceOfFaceOfCoin, Candidate
from library.database import append_default_record_to_df_even, get_df_even, get_df_p, df_even_to_csv
from library.views import print_even_series_rule


# 探索の上限
LIMIT_SPAN = 1001

# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 60

# CSV保存用タイマー
start_time_for_save = None
is_dirty_csv = False


def update_dataframe(df, spec, best_p, best_p_error, best_series_rule_if_it_exists,
        latest_p, latest_p_error, latest_series_rule, candidates):
    """データフレーム更新
    
    Parameters
    ----------
    spec : Specification
        ［仕様］
    """

    global start_time_for_save, is_dirty_csv

    # # 表示
    # print_even_series_rule(
    #         p=p,
    #         best_p=best_p,
    #         best_p_error=best_p_error,
    #         series_rule=best_series_rule_if_it_exists)

    # ［試行シリーズ数］列を更新
    #
    #   NOTE best と latest のどちらにも同じ値が入っているはずです
    #
    df.loc[df['p']==spec.p, ['trials_series']] = latest_series_rule.trials_series

    # ［調整後の表が出る確率］列を更新
    df.loc[df['p']==spec.p, ['best_p']] = best_p
    df.loc[df['p']==spec.p, ['latest_p']] = latest_p

    # ［調整後の表が出る確率の５割との誤差］列を更新
    df.loc[df['p']==spec.p, ['best_p_error']] = best_p_error
    df.loc[df['p']==spec.p, ['latest_p_error']] = latest_p_error

    # ［表勝ち１つの点数］列を更新
    df.loc[df['p']==spec.p, ['best_p_step']] = best_series_rule_if_it_exists.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)
    df.loc[df['p']==spec.p, ['latest_p_step']] = latest_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)

    # ［裏勝ち１つの点数］列を更新
    df.loc[df['p']==spec.p, ['best_q_step']] = best_series_rule_if_it_exists.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)
    df.loc[df['p']==spec.p, ['latest_q_step']] = latest_series_rule.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)

    # ［目標の点数］列を更新 
    df.loc[df['p']==spec.p, ['best_span']] = best_series_rule_if_it_exists.step_table.span
    df.loc[df['p']==spec.p, ['latest_span']] = latest_series_rule.step_table.span

    # ［シリーズ・ルール候補］列を更新
    df.loc[df['p']==spec.p, ['candidates']] = candidates

    is_dirty_csv = True


def ready_records(df, specified_failure_rate, turn_system, generation_algorythm, specified_trials_series):
    """EVENテーブルについて、まず、行の存在チェック。無ければ追加"""
    is_append_new_record = False

    df_p = get_df_p()

    # ［コインを投げて表が出る確率］
    for p in df_p['p']:
        # 存在しなければデフォルトのレコード追加
        if not ((df['p'] == p) & (df['failure_rate'] == specified_failure_rate) & (df['trials_series'] == specified_trials_series)).any():

            # ［仕様］
            spec = Specification(
                    p=p,
                    failure_rate=specified_failure_rate,
                    turn_system=turn_system)
            
            append_default_record_to_df_even(
                    df=df,
                    spec=spec,
                    trials_series=specified_trials_series)
            is_append_new_record = True

    if is_append_new_record:
        # CSV保存
        df_even_to_csv(df=df, failure_rate=specified_failure_rate, turn_system=turn_system, generation_algorythm=generation_algorythm, trials_series=specified_trials_series)


def iteration_deeping(df, specified_failure_rate, specified_turn_system, specified_trials_series, specified_abs_small_error, current_abs_lower_limit_of_error, generation_algorythm, passage_upper_limit):
    """反復深化探索の１セット

    Parameters
    ----------
    df : DataFrame
        データフレーム
    current_abs_lower_limit_of_error : float
        下限
    
    Returns
    -------
    is_update_table : bool
        更新が有ったか？
    number_of_target : int
        処理対象の数
    number_of_smalled : int
        処理完了の数
    number_of_yield : int
        処理を途中で譲った数
    """

    global start_time_for_save, is_dirty_csv

    is_update_table = False

    # まず、行の存在チェック。無ければ追加
    ready_records(df=df, specified_failure_rate=specified_failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm, specified_trials_series=specified_trials_series)


    # NOTE ［試行シリーズ数］が違うものを１つのファイルに混ぜたくない。ファイルを分けてある


    number_of_target = 0        # 処理対象の数
    number_of_smalled = 0       # 処理完了の数
    number_of_yield = 0         # 処理を途中で譲った数
    number_of_passaged = 0      # 空振りで終わったレコード数


    for         p,       failure_rate,       turn_system,       trials_series,       best_p,       best_p_error,       best_p_step,       best_q_step,       best_span,       latest_p,       latest_p_error,       latest_p_step,       latest_q_step,       latest_span,       candidates in\
        zip(df['p'], df['failure_rate'], df['turn_system'], df['trials_series'], df['best_p'], df['best_p_error'], df['best_p_step'], df['best_q_step'], df['best_span'], df['latest_p'], df['latest_p_error'], df['latest_p_step'], df['latest_q_step'], df['latest_span'], df['candidates']):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        trials_series = round_letro(trials_series)
        best_p_step = round_letro(best_p_step)
        best_q_step = round_letro(best_q_step)
        best_span = round_letro(best_span)
        latest_p_step = round_letro(latest_p_step)
        latest_q_step = round_letro(latest_q_step)
        latest_span = round_letro(latest_span)


        # FIXME 自明のチェック。１つのファイルには、同じ［将棋の引分け率］のデータしかない
        if specified_failure_rate != failure_rate:
            raise ValueError(f"{specified_failure_rate=} != {failure_rate=}")


        # FIXME 自明のチェック。 specified_trials_series と trials_series は必ず一致する
        if specified_trials_series != trials_series:
            raise ValueError(f"{specified_trials_series=} != {trials_series=}")


        # ここから先、処理対象行
        number_of_target += 1


        # 仕様
        spec = Specification(
                p=p,
                failure_rate=specified_failure_rate,
                turn_system=specified_turn_system)

        # ダミー値。ベスト値が見つかっていないときは、この値は使えない値です
        best_series_rule_if_it_exists = SeriesRule.make_series_rule_base(
                spec=spec,
                trials_series=trials_series,
                p_step=best_p_step,
                q_step=best_q_step,
                span=best_span)

        update_count = 0
        passage_count = 0
        is_cutoff = False
        is_good = False


        # 既存データの方が信用のおけるデータだった場合、スキップ
        # エラーが十分小さければスキップ
        if abs(best_p_error) <= specified_abs_small_error:
            is_automatic = False

            # FIXME 全部のレコードがスキップされたとき、無限ループに陥る
            number_of_smalled += 1

        # アルゴリズムで求めるケース
        else:
            #print(f"[p={p}]", end='', flush=True)
            is_automatic = True

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
                                spec=spec,
                                trials_series=trials_series,
                                p_step=cur_p_step,
                                q_step=cur_q_step,
                                span=cur_span)


                        # 力任せ探索の場合                        
                        if generation_algorythm == BRUTE_FORCE:
                            list_of_trial_results_for_one_series = []

                            for i in range(0, specified_trials_series):

                                # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
                                list_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                                        spec=spec,
                                        upper_limit_coins=latest_series_rule.upper_limit_coins)

                                # FIXME 検証
                                if len(list_of_face_of_coin) < latest_series_rule.shortest_coins:
                                    text = f"{spec.p=} 指定の対局シートの長さ {len(list_of_face_of_coin)} は、最短対局数の理論値 {latest_series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
                                    print(f"""{text}
{list_of_face_of_coin=}
{latest_series_rule.upper_limit_coins=}
""")
                                    raise ValueError(text)


                                # 疑似のリストをもとに、シリーズとして見てみる
                                trial_results_for_one_series = judge_series(
                                        spec=spec,
                                        series_rule=latest_series_rule,
                                        list_of_face_of_coin=list_of_face_of_coin)
                                
                                list_of_trial_results_for_one_series.append(trial_results_for_one_series)
                            
                            # シミュレーションの結果
                            large_series_trial_summary = LargeSeriesTrialSummary(
                                    list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)

                            # Ａさんが勝った回数
                            s_wins_a = large_series_trial_summary.wins(challenged=SUCCESSFUL, winner=ALICE)
                            f_wins_a = large_series_trial_summary.wins(challenged=FAILED, winner=ALICE)
                            latest_p = (s_wins_a + f_wins_a) / specified_trials_series
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
                            is_update_table = True
                            update_count += 1
                            best_p = latest_p
                            best_p_error = latest_p_error
                            best_series_rule_if_it_exists = latest_series_rule

                            # ［シリーズ・ルール候補］
                            candidate_obj = Candidate(
                                    p_error=best_p_error,
                                    trials_series=specified_trials_series,
                                    p_step=best_series_rule_if_it_exists.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD),   # FIXME FAILED の方は記録しなくていい？
                                    q_step=best_series_rule_if_it_exists.step_table.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL),
                                    span=best_series_rule_if_it_exists.step_table.span,
                                    shortest_coins=best_series_rule_if_it_exists.shortest_coins,             # ［最短対局数］
                                    upper_limit_coins=best_series_rule_if_it_exists.upper_limit_coins)       # ［上限対局数］
                            candidate_str = candidate_obj.as_str()
                            print(f"[{datetime.datetime.now()}][p={p*100:3.0f}％  failure_rate={specified_failure_rate*100:3.0f}％  turn_system={Converter.turn_system_to_code(turn_system)}] {candidate_str}", flush=True) # すぐ表示

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
                                    spec=spec,
                                    best_p=best_p,
                                    best_p_error=best_p_error,
                                    best_series_rule_if_it_exists=best_series_rule_if_it_exists,
                                    latest_p=latest_p,
                                    latest_p_error=latest_p_error,
                                    latest_series_rule=latest_series_rule,
                                    candidates=candidates)

                            # 指定間隔（秒）で保存
                            end_time_for_save = time.time()
                            if is_dirty_csv and INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                                start_time_for_save = end_time_for_save
                                is_dirty_csv = False

                                # CSV保存
                                print(f"[{datetime.datetime.now()}] CSV保存 ...")
                                df_even_to_csv(df=df, failure_rate=spec.failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm, trials_series=specified_trials_series)


                            # 十分な答えが出たか、複数回の更新があったとき、探索を打ち切ります
                            if abs(best_p_error) < current_abs_lower_limit_of_error or 2 < update_count:
                                is_good = True
                                is_cutoff = True
                                number_of_yield += 1
                                # # 進捗バー
                                # print('cutoff (good)', flush=True)
                                break

                        else:
                            passage_count += 1
                            latest_candidates = candidates

                            # # 進捗バー
                            # print('.', end='', flush=True)

                            # 空振りが多いとき、探索を打ち切ります
                            if passage_upper_limit < passage_count:
                                is_cutoff = True
                                number_of_passaged += 1

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
                    spec=spec,
                    best_p=best_p,
                    best_p_error=best_p_error,
                    best_series_rule_if_it_exists=best_series_rule_if_it_exists,
                    latest_p=latest_p,
                    latest_p_error=latest_p_error,
                    latest_series_rule=latest_series_rule,
                    candidates=latest_candidates)

            # 指定間隔（秒）で保存
            end_time_for_save = time.time()
            if is_dirty_csv and INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - start_time_for_save:
                start_time_for_save = end_time_for_save
                is_dirty_csv = False

                # CSV保存
                print(f"[{datetime.datetime.now()}] CSV保存 ...")
                df_even_to_csv(df=df, failure_rate=spec.failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm, trials_series=specified_trials_series)


    return is_update_table, number_of_target, number_of_smalled, number_of_yield, number_of_passaged


def automatic(specified_failure_rate, specified_turn_system, generation_algorythm, specified_trials_series, specified_abs_small_error):

    global start_time_for_save, is_dirty_csv

    df_ev = get_df_even(failure_rate=specified_failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm, trials_series=specified_trials_series)
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

    speed = 10
    current_abs_lower_limit_of_error = ABS_OUT_OF_ERROR
    passage_upper_limit = 10

    # ループに最初に１回入るためだけの設定
    worst_abs_best_p_error = ABS_OUT_OF_ERROR

    # １件もデータがない、または
    # 指定の誤差の最小値より、誤差が大きい間繰り返す
    #
    #   NOTE データ件数が０件だと、誤差の最大値が nan になってしまう。データは生成される前提
    #
    while len(df_ev) < 1 or specified_abs_small_error < worst_abs_best_p_error:
        # ［エラー］列で一番大きい値を取得します
        #
        #   ［調整後の表が出る確率］を 0.5 になるように目指します。［エラー］列は、［調整後の表が出る確率］と 0.5 の差の絶対値です
        #
        best_p_error_min = df_ev['best_p_error'].min()
        best_p_error_max = df_ev['best_p_error'].max()
        worst_abs_best_p_error = max(abs(best_p_error_min), abs(best_p_error_max))


        # データが１件も入っていないとき、 nan になってしまう。とりあえずワースト誤差を最大に設定する
        if pd.isnull(worst_abs_best_p_error):
            worst_abs_best_p_error = ABS_OUT_OF_ERROR


        # とりあえず、［調整後の表が出る確率］が［最大エラー］値の半分未満になるよう目指す
        #
        #   NOTE P=0.99 の探索は、 p=0.50～0.98 を全部合わせた処理時間よりも、時間がかかるかも。だから p=0.99 のケースだけに合わせて時間調整するといいかも。
        #   NOTE エラー値を下げるときに、８本勝負の次に９本勝負を見つけられればいいですが、そういうのがなく次が１５本勝負だったりするような、跳ねるケースでは処理が長くなりがちです。リミットをゆっくり下げればいいですが、どれだけ気を使っても避けようがありません
        #
        #   TODO 探索をタイムシェアリングのために途中で譲ったのか、更新が終わってるのかを区別したい
        #
        is_update_table, number_of_target, number_of_smalled, number_of_yield, number_of_passaged = iteration_deeping(
                df=df_ev,
                specified_failure_rate=specified_failure_rate,
                specified_turn_system=specified_turn_system,
                specified_trials_series=specified_trials_series,
                specified_abs_small_error=specified_abs_small_error,

                current_abs_lower_limit_of_error=current_abs_lower_limit_of_error,

                generation_algorythm=generation_algorythm,
                passage_upper_limit=passage_upper_limit)


        #
        # NOTE 小数点以下の桁を長く出しても見づらい
        #
        print(f"[{datetime.datetime.now()}][failure_rate={specified_failure_rate}]  update={is_update_table}  target={number_of_target}  smalled={number_of_smalled}  yield={number_of_yield}  passaged={number_of_passaged}  {speed=}  worst_error={worst_abs_best_p_error:.7f}(min={best_p_error_min}  max={best_p_error_max})  current_error={current_abs_lower_limit_of_error:.7f}  small_error={specified_abs_small_error:.7f}  {passage_upper_limit=}")


        # 処理が完了したから、ループを抜ける
        if number_of_target == number_of_smalled:
            print(f"すべてのデータについて、誤差が {specified_abs_small_error} 以下になるよう作成完了。 {worst_abs_best_p_error=}")
            break


        # タイムシェアリングのために、処理を譲ることがオーバーヘッドになってきそうなら        
        if 0 < number_of_passaged:
            # 初期値が 10 なら 1.1 倍で必ず 1 は増える
            passage_upper_limit = int(passage_upper_limit * 1.1)

        else:
            passage_upper_limit = int(passage_upper_limit * 0.9)
            if  passage_upper_limit < 10:
                passage_upper_limit = 10

            # タイムシェアリングのために、処理を譲っているというわけでもないとき
            if number_of_yield < 1:
                # スピードがどんどん上がっていく
                if not is_update_table:
                    speed += 1

                    # 半分、半分でも速そうなので、１０分の９を繰り返す感じで。
                    if current_abs_lower_limit_of_error is None:
                        current_abs_lower_limit_of_error = worst_abs_best_p_error * 9/speed
                    else:
                        current_abs_lower_limit_of_error *= 9/speed
                    
                    if current_abs_lower_limit_of_error < specified_abs_small_error:
                        current_abs_lower_limit_of_error = specified_abs_small_error


    print(f"ループから抜けました")


    if is_dirty_csv:
        is_dirty_csv = False

        # 最後に CSV保存
        print(f"[{datetime.datetime.now()}] 最後に CSV保存 ...")
        df_even_to_csv(df=df_ev, failure_rate=specified_failure_rate, turn_system=specified_turn_system, generation_algorythm=generation_algorythm, trials_series=specified_trials_series)


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の引分け率］を尋ねる
        prompt = f"""\
What is the failure rate?
Example: 10% is 0.1
? """
        specified_failure_rate = float(input(prompt))


        # ［先後の決め方］を尋ねる
        prompt = f"""\
(1) Frozen turn
(2) Alternating turn
Which one(1-2)? """
        choice = input(prompt)
        if choice == '1':
            specified_turn_system = FROZEN_TURN
        elif choice == '2':
            specified_turn_system = ALTERNATING_TURN
        else:
            raise ValueError(f"{choice=}")


        generation_algorythm = Converter.make_generation_algorythm(failure_rate=specified_failure_rate, turn_system=specified_turn_system)
        if generation_algorythm == BRUTE_FORCE:
            print("力任せ探索を行います")

            # ［試行シリーズ数］を尋ねる
            prompt = f"""\
How many times do you want to try the series?

(0) Try       2 series
(1) Try      20 series
(2) Try     200 series
(3) Try    2000 series
(4) Try   20000 series
(5) Try  200000 series
(6) Try 2000000 series

Example: 3
(0-6)? """
            precision = int(input(prompt))
            specified_trials_series = Converter.precision_to_trials_series(precision)
            specified_abs_small_error = Converter.precision_to_small_error(precision)

        elif generation_algorythm == THEORETICAL:
            print("理論値を求めます。便宜的に試行回数は 1 と記入することにします")
            specified_trials_series = 1
            specified_abs_small_error = 0.0000009   # 便宜的

        else:
            raise ValueError(f"{generation_algorythm=}")


        automatic(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system=specified_turn_system,
                generation_algorythm=generation_algorythm,
                specified_trials_series=specified_trials_series,
                specified_abs_small_error=specified_abs_small_error)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
