#
# 生成
# python generate_even.py
#
#   TODO 実際値ではなく、理論値を記録したい。 alternating_turn の方がそれに対応してない
#
#   ［表勝ちだけでの対局数］と、［裏勝ちだけでの対局数］を探索する。
#

import traceback
import random
import math
import pandas as pd

from library import HEAD, TAIL, ALICE, SUCCESSFUL, WHEN_FROZEN_TURN, WHEN_ALTERNATING_TURN, round_letro, PseudoSeriesResult, judge_series, PointsConfiguration, calculate_probability, LargeSeriesTrialSummary, Specification
from file_paths import get_even_csv_file_path
from database import append_default_record_to_df_even, get_df_even, get_df_p
from views import print_even


# このラウンド数を満たさないデータは、再探索します
REQUIRED_MUMBER_OF_SERIES = 2_000_000

# 勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
ABS_OUT_OF_ERROR = 0.51

# 十分小さいエラー
ABS_SMALL_ERROR = 0.00009

# 探索の上限
LIMIT_SPAN = 1001


def update_dataframe(df, p, failure_rate,
        best_p, best_p_error, best_number_of_series, best_pts_conf,
        latest_p, latest_p_error, latest_number_of_series, latest_pts_conf, process,
        turn_system):
    """データフレーム更新"""

    # 表示
    print_even(
            p=p,
            best_p=best_p,
            best_p_error=best_p_error,
            best_number_of_series=best_number_of_series,
            pts_conf=best_pts_conf)

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
    df.loc[df['p']==p, ['best_p_step']] = best_pts_conf.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)
    df.loc[df['p']==p, ['latest_p_step']] = latest_pts_conf.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)

    # ［裏勝ち１つの点数］列を更新
    df.loc[df['p']==p, ['best_q_step']] = best_pts_conf.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)
    df.loc[df['p']==p, ['latest_q_step']] = latest_pts_conf.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)

    # ［目標の点数］列を更新 
    df.loc[df['p']==p, ['best_span']] = best_pts_conf.span
    df.loc[df['p']==p, ['latest_span']] = latest_pts_conf.span

    # ［計算過程］列を更新
    df.loc[df['p']==p, ['process']] = process

    # CSV保存
    df.to_csv(
            get_even_csv_file_path(turn_system=turn_system),
            # ［計算過程］列は長くなるので末尾に置きたい
            columns=['p', 'failure_rate', 'best_p', 'best_p_error', 'best_number_of_series', 'best_p_step', 'best_q_step', 'best_span', 'latest_p', 'latest_p_error', 'latest_number_of_series', 'latest_p_step', 'latest_q_step', 'latest_span', 'process'],
            index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


def iteration_deeping(df, abs_limit_of_error, specified_failure_rate, turn_system):
    """反復深化探索の１セット

    Parameters
    ----------
    df : DataFrame
        データフレーム
    abs_limit_of_error : float
        リミット
    """

    is_append_new_record = False

    # まず、存在チェック。無ければ追加
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
        df.to_csv(
                get_even_csv_file_path(turn_system=turn_system),
                # ［計算過程］列は長くなるので末尾に置きたい
                columns=['p', 'failure_rate', 'best_p', 'best_p_error', 'best_number_of_series', 'best_p_step', 'best_q_step', 'best_span', 'latest_p', 'latest_p_error', 'latest_number_of_series', 'latest_p_step', 'latest_q_step', 'latest_span', 'process'],
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


    for         p,       failure_rate,       best_p,       best_p_error,       best_number_of_series,       best_p_step,       best_q_step,       best_span,       latest_p,       latest_p_error,       latest_number_of_series,       latest_p_step,       latest_q_step,       latest_span,       process in\
        zip(df['p'], df['failure_rate'], df['best_p'], df['best_p_error'], df['best_number_of_series'], df['best_p_step'], df['best_q_step'], df['best_span'], df['latest_p'], df['latest_p_error'], df['latest_number_of_series'], df['latest_p_step'], df['latest_q_step'], df['latest_span'], df['process']):

        # NOTE pandas では数は float 型で入っているので、 int 型に再変換してやる必要がある
        best_p_step = round_letro(best_p_step)
        best_q_step = round_letro(best_q_step)
        best_span = round_letro(best_span)
        latest_p_step = round_letro(latest_p_step)
        latest_q_step = round_letro(latest_q_step)
        latest_span = round_letro(latest_span)


        # 該当行以外は無視
        if specified_failure_rate != failure_rate:
            continue


        # ［かくきんシステムのｐの構成］
        if 0 < best_p_step:
            temp_best_p_step = best_p_step
        else:
            temp_best_p_step = 1

        best_pts_conf = PointsConfiguration(
                failure_rate=failure_rate,
                turn_system=turn_system,
                p_step=temp_best_p_step,
                q_step=best_q_step,
                span=best_span)

        update_count = 0
        passage_count = 0
        is_cutoff = False
        is_good = False

        # 既存データの方が信用のおけるデータだった場合、スキップ
        # エラーが十分小さければスキップ
        if REQUIRED_MUMBER_OF_SERIES < best_number_of_series or abs(best_p_error) <= ABS_SMALL_ERROR:
            is_automatic = False

        # アルゴリズムで求めるケース
        else:
            print(f"[p={p}]", end='', flush=True)
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

                        # ［かくきんシステムのｐの構成］
                        latest_pts_conf = PointsConfiguration(
                                failure_rate=failure_rate,
                                turn_system=spec.turn_system,
                                p_step=cur_p_step,
                                q_step=cur_q_step,
                                span=cur_span)


                        if spec.turn_system == WHEN_FROZEN_TURN:
                            # NOTE 理論値の場合
                            latest_p = calculate_probability(
                                    p=p,
                                    H=latest_pts_conf.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                                    T=latest_pts_conf.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))
                            latest_p_error = latest_p - 0.5


                        if abs(latest_p_error) < abs(best_p_error):
                            update_count += 1
                            best_p = latest_p
                            best_p_error = latest_p_error
                            best_pts_conf = latest_pts_conf

                            # ［最短対局数］［最長対局数］
                            shortest_time = best_pts_conf.number_shortest_time()
                            longest_time = best_pts_conf.number_longest_time()

                            # 計算過程
                            one_process_text = f'[{best_p_error:.6f} {best_pts_conf.get_step_by(challenged=SUCCESSFUL, face_of_coin=HEAD)}表 {best_pts_conf.get_step_by(challenged=SUCCESSFUL, face_of_coin=TAIL)}裏 {best_pts_conf.span}目 {shortest_time}～{longest_time}局]'
                            print(one_process_text, end='', flush=True) # すぐ表示

                            # ［計算過程］列を更新
                            #
                            #   途中の計算式。半角空裏区切り
                            #
                            if isinstance(process, str):
                                process = f"{process} {one_process_text}"
                            else:
                                process = one_process_text

                            # 表示とデータフレーム更新
                            update_dataframe(
                                    df=df,
                                    p=p,
                                    failure_rate=failure_rate,
                                    best_p=best_p,
                                    best_p_error=best_p_error,
                                    best_number_of_series=REQUIRED_MUMBER_OF_SERIES,
                                    best_pts_conf=best_pts_conf,
                                    latest_p=latest_p,
                                    latest_p_error=latest_p_error,
                                    latest_number_of_series=REQUIRED_MUMBER_OF_SERIES,
                                    latest_pts_conf=latest_pts_conf,
                                    process=process,
                                    turn_system=spec.turn_system)

                            # 十分な答えが出たか、複数回の更新があったとき、探索を打ち切ります
                            if abs(best_p_error) < abs_limit_of_error or 2 < update_count:
                                is_good = True
                                is_cutoff = True
                                # 進捗バー
                                print('cutoff (good)', flush=True)
                                break

                        else:
                            passage_count += 1
                            latest_process = process

                            # 進捗バー
                            print('.', end='', flush=True)

                            # 空振りが多いとき、探索を打ち切ります
                            if 30 < passage_count:
                                is_cutoff = True
                                # 進捗バー
                                print('cutoff (procrastinate)', flush=True)
                                break

                    start_p_step = 1

                    if is_cutoff:
                        break

                start_q_step = 1

                if is_cutoff:
                    break

            print() # 改行


        if is_good:
            continue

        # 自動計算未完了
        if is_automatic and best_p_error == ABS_OUT_OF_ERROR:
            print(f"先手勝率：{p*100:2} ％  （自動計算未完了）")

        elif update_count < 1:
            print(f"先手勝率：{p*100:2} ％  （更新なし）")

        # 空振りが１回でもあれば、途中状態を保存
        if 0 < passage_count:
            # 表示とデータフレーム更新
            update_dataframe(
                    df=df,
                    p=p,
                    failure_rate=failure_rate,
                    best_p=best_p,
                    best_p_error=best_p_error,
                    best_number_of_series=REQUIRED_MUMBER_OF_SERIES,
                    best_pts_conf=best_pts_conf,
                    latest_p=latest_p,
                    latest_p_error=latest_p_error,
                    latest_number_of_series=REQUIRED_MUMBER_OF_SERIES,
                    latest_pts_conf=latest_pts_conf,
                    process=latest_process,
                    turn_system=turn_system)


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


#         print(f"""\
# What is the probability of flipping a coin and getting heads?
# Example: 70% is 0.7
# ? """)
#         p = float(input())


        print(f"""\
What is the failure rate?
Example: 10% is 0.1
? """)
        failure_rate = float(input())


        df_ev = get_df_even(turn_system=turn_system)
        print(df_ev)


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
            print(f"{worst_abs_best_p_error=}")

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
                    specified_failure_rate=failure_rate,
                    turn_system=turn_system)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
