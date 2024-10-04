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

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FAILED, FROZEN_TURN, ALTERNATING_TURN, BRUTE_FORCE, THEORETICAL, OUT_OF_P, ABS_OUT_OF_ERROR, EVEN, UPPER_LIMIT_OF_P, Converter, round_letro, judge_series, SeriesRule, calculate_probability, LargeSeriesTrialSummary, Specification, SequenceOfFaceOfCoin, Candidate
from library.database import EvenTable
from library.views import print_even_series_rule


# 探索の上限
LIMIT_SPAN = 1001

# CSV保存間隔（秒）
INTERVAL_SECONDS_FOR_SAVE_CSV = 60


class Automation():
    """自動化"""


    def __init__(self, specified_failure_rate, specified_turn_system, generation_algorythm, specified_trials_series, specified_abs_small_error):
        self._specified_failure_rate=specified_failure_rate
        self._specified_turn_system=specified_turn_system
        self._generation_algorythm=generation_algorythm
        self._specified_trials_series=specified_trials_series
        self._specified_abs_small_error=specified_abs_small_error

        self._df_ev = None
        self._current_abs_lower_limit_of_error = None
        self._passage_upper_limit = None

        self._start_time_for_save = None    # CSV保存用タイマー
        self._is_dirty_csv = False

        self._number_of_target = None       # 処理対象の数
        self._number_of_smalled = None      # 処理完了の数
        self._number_of_yield = None        # 処理を途中で譲った数
        self._number_of_passaged = None     # 空振りで終わったレコード数


    def update_dataframe(self, spec, best_p, best_p_error, best_series_rule_if_it_exists,
            latest_p, latest_p_error, latest_series_rule, candidates):
        """データフレーム更新
        
        Parameters
        ----------
        spec : Specification
            ［仕様］
        """

        # # 表示
        # print_even_series_rule(
        #         p=p,
        #         best_p=best_p,
        #         best_p_error=best_p_error,
        #         series_rule=best_series_rule_if_it_exists)

        EvenTable.update_record(
                df=self._df_ev,
                specified_p = spec.p,
                trials_series=latest_series_rule.trials_series,     # NOTE best と latest のどちらにも同じ値が入っているはずです
                best_p=best_p,
                best_p_error=best_p_error,
                best_h_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=HEAD),
                best_t_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=TAIL),
                best_span=best_series_rule_if_it_exists.step_table.span,
                latest_p=latest_p,
                latest_p_error=latest_p_error,
                latest_h_step=latest_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                latest_t_step=latest_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                latest_span=latest_series_rule.step_table.span,
                candidates=candidates)

        self._is_dirty_csv = True


    def ready_records(self):
        """EVENテーブルについて、まず、行の存在チェック。無ければ追加"""
        is_append_new_record = False

        # ［コインを投げて表が出る確率］
        for p_parcent in range(int(EVEN * 100), int(UPPER_LIMIT_OF_P * 100) + 1):
            p = p_parcent / 100
            
            # 存在しなければデフォルトのレコード追加
            if not ((self._df_ev['p'] == p) & (self._df_ev['failure_rate'] == self._specified_failure_rate) & (self._df_ev['trials_series'] == self._specified_trials_series)).any():

                # ［仕様］
                spec = Specification(
                        p=p,
                        failure_rate=self._specified_failure_rate,
                        turn_system=self._specified_turn_system)
                
                EvenTable.append_default_record(
                        spec=spec,
                        trials_series=self._specified_trials_series)
                is_append_new_record = True

        if is_append_new_record:
            # CSV保存
            EvenTable.to_csv(
                    df=self._df_ev,
                    failure_rate=self._specified_failure_rate,
                    turn_system=self._specified_turn_system,
                    generation_algorythm=self._generation_algorythm,
                    trials_series=self._specified_trials_series)


    def on_each(self, record):

        # FIXME 自明のチェック。１つのファイルには、同じ［将棋の引分け率］のデータしかない
        if self._specified_failure_rate != record.failure_rate:
            raise ValueError(f"{self._specified_failure_rate=} != {record.failure_rate=}")


        if self._specified_turn_system != Converter.code_to_turn_system(record.turn_system_str):
            raise ValueError(f"{Converter.turn_system_to_code(self._specified_turn_system)=} != {record.turn_system_str=}")


        # FIXME 自明のチェック。 self._specified_trials_series と record.trials_series は必ず一致する
        if self._specified_trials_series != record.trials_series:
            raise ValueError(f"{self._specified_trials_series=} != {record.trials_series=}")


        # どんどん更新されていく
        best_p = record.best_p
        best_p_error = record.best_p_error
        latest_p = record.latest_p
        latest_p_error = record.latest_p_error
        candidates = record.candidates


        # ここから先、処理対象行
        self._number_of_target += 1


        # 仕様
        spec = Specification(
                p=record.p,
                failure_rate=record.failure_rate,
                turn_system=self._specified_turn_system)

        # ダミー値。ベスト値が見つかっていないときは、この値は使えない値です
        best_series_rule_if_it_exists = SeriesRule.make_series_rule_base(
                spec=spec,
                trials_series=record.trials_series,
                h_step=record.best_h_step,
                t_step=record.best_t_step,
                span=record.best_span)

        update_count = 0
        passage_count = 0
        is_cutoff = False
        is_good = False


        # 既存データの方が信用のおけるデータだった場合、スキップ
        # エラーが十分小さければスキップ
        if abs(best_p_error) <= self._specified_abs_small_error:
            is_automatic = False

            # FIXME 全部のレコードがスキップされたとき、無限ループに陥る
            self._number_of_smalled += 1

        # アルゴリズムで求めるケース
        else:
            #print(f"[p={spec.p}]", end='', flush=True)
            is_automatic = True

            #
            # ［目標の点数］、［裏番で勝ったときの勝ち点］、［表番で勝ったときの勝ち点］を１つずつ進めていく探索です。
            #
            # ［目標の点数］＞＝［裏番で勝ったときの勝ち点］＞＝［表番で勝ったときの勝ち点］という関係があります。
            #
            start_t_step = record.latest_t_step
            start_h_step = record.latest_h_step + 1      # 終わっているところの次から始める      NOTE h_step の初期値は 0 であること
            for cur_span in range(record.latest_span, LIMIT_SPAN):
                for cur_t_step in range(start_t_step, cur_span + 1):
                    for cur_h_step in range(start_h_step, cur_t_step + 1):

                        # ［シリーズ・ルール］
                        latest_series_rule = SeriesRule.make_series_rule_base(
                                spec=spec,
                                trials_series=record.trials_series,
                                h_step=cur_h_step,
                                t_step=cur_t_step,
                                span=cur_span)


                        # 力任せ探索の場合                        
                        if self._generation_algorythm == BRUTE_FORCE:
                            list_of_trial_results_for_one_series = []

                            for i in range(0, self._specified_trials_series):

                                # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
                                path_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                                        spec=spec,
                                        upper_limit_coins=latest_series_rule.upper_limit_coins)

                                # FIXME 検証
                                if len(path_of_face_of_coin) < latest_series_rule.shortest_coins:
                                    text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {latest_series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
                                    print(f"""{text}
{path_of_face_of_coin=}
{latest_series_rule.upper_limit_coins=}
""")
                                    raise ValueError(text)


                                # 疑似のリストをもとに、シリーズとして見てみる
                                trial_results_for_one_series = judge_series(
                                        spec=spec,
                                        series_rule=latest_series_rule,
                                        path_of_face_of_coin=path_of_face_of_coin)
                                
                                list_of_trial_results_for_one_series.append(trial_results_for_one_series)
                            
                            # シミュレーションの結果
                            large_series_trial_summary = LargeSeriesTrialSummary(
                                    list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)

                            # Ａさんが勝った回数
                            s_wins_a = large_series_trial_summary.wins(challenged=SUCCESSFUL, winner=ALICE)
                            f_wins_a = large_series_trial_summary.wins(challenged=FAILED, winner=ALICE)
                            latest_p = (s_wins_a + f_wins_a) / self._specified_trials_series
                            latest_p_error = latest_p - 0.5


                        # 理論値の場合
                        elif self._generation_algorythm == THEORETICAL:

                            # オーバーフロー例外に対応したプログラミングをすること
                            latest_p, err = calculate_probability(
                                    p=spec.p,
                                    H=latest_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=HEAD),
                                    T=latest_series_rule.step_table.get_time_by(challenged=SUCCESSFUL, face_of_coin=TAIL))
                            
                            # FIXME とりあえず、エラーが起こっている場合は、あり得ない値をセットして計算を完了させておく
                            if err is not None:
                                latest_p_error = 0      # 何度計算しても失敗するだろうから、計算完了するようにしておく
                            else:
                                latest_p_error = latest_p - 0.5


                        else:
                            raise ValueError(f"{self._generation_algorythm=}")


                        if abs(latest_p_error) < abs(best_p_error):
                            is_update_table = True
                            update_count += 1
                            best_p = latest_p
                            best_p_error = latest_p_error
                            best_series_rule_if_it_exists = latest_series_rule

                            # ［シリーズ・ルール候補］
                            candidate_obj = Candidate(
                                    p_error=best_p_error,
                                    trials_series=record.trials_series,
                                    h_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=HEAD),   # FIXME FAILED の方は記録しなくていい？
                                    t_step=best_series_rule_if_it_exists.step_table.get_step_by(face_of_coin=TAIL),
                                    span=best_series_rule_if_it_exists.step_table.span,
                                    shortest_coins=best_series_rule_if_it_exists.shortest_coins,             # ［最短対局数］
                                    upper_limit_coins=best_series_rule_if_it_exists.upper_limit_coins)       # ［上限対局数］
                            candidate_str = candidate_obj.as_str()
                            print(f"[{datetime.datetime.now()}][p={spec.p * 100:3.0f}％  failure_rate={spec.failure_rate * 100:3.0f}％  turn_system={record.turn_system_str}] {candidate_str}", flush=True) # すぐ表示

                            # ［シリーズ・ルール候補］列を更新
                            #
                            #   途中の計算式。半角空裏区切り
                            #
                            if isinstance(candidates, str):
                                candidates = f"{candidates} {candidate_str}"
                            else:
                                candidates = candidate_str

                            # 表示とデータフレーム更新
                            self.update_dataframe(
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
                            if self._is_dirty_csv and INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - self._start_time_for_save:
                                self._start_time_for_save = end_time_for_save
                                self._is_dirty_csv = False

                                # CSV保存
                                print(f"[{datetime.datetime.now()}] CSV保存 ...")
                                EvenTable.to_csv(df=df, failure_rate=spec.failure_rate, turn_system=self._specified_turn_system, generation_algorythm=self._generation_algorythm, trials_series=record.trials_series)


                            # 十分な答えが出たか、複数回の更新があったとき、探索を打ち切ります
                            if abs(best_p_error) < self._current_abs_lower_limit_of_error or 2 < update_count:
                                is_good = True
                                is_cutoff = True
                                self._number_of_yield += 1
                                # # 進捗バー
                                # print('cutoff (good)', flush=True)
                                break

                        else:
                            passage_count += 1
                            latest_candidates = candidates

                            # # 進捗バー
                            # print('.', end='', flush=True)

                            # 空振りが多いとき、探索を打ち切ります
                            if self._passage_upper_limit < passage_count:
                                is_cutoff = True
                                self._number_of_passaged += 1

                                # # 進捗バー
                                # print('cutoff (procrastinate)', flush=True)
                                break

                    start_h_step = 1

                    if is_cutoff:
                        break

                start_t_step = 1

                if is_cutoff:
                    break

            # print() # 改行


        # 続行
        if is_good:
            return
            #continue


        # 空振りが１回でもあれば、途中状態を保存
        if 0 < passage_count:
            # 表示とデータフレーム更新
            self.update_dataframe(
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
            if self._is_dirty_csv and INTERVAL_SECONDS_FOR_SAVE_CSV < end_time_for_save - self._start_time_for_save:
                self._start_time_for_save = end_time_for_save
                self._is_dirty_csv = False

                # CSV保存
                print(f"[{datetime.datetime.now()}] CSV保存 ...")
                EvenTable.to_csv(df=self._df_ev, failure_rate=spec.failure_rate, turn_system=self._specified_turn_system, generation_algorythm=self._generation_algorythm, trials_series=record.trials_series)


    def iteration_deeping(self):
        """反復深化探索の１セット
        
        Returns
        -------
        is_update_table : bool
            更新が有ったか？
        """

        is_update_table = False

        # まず、行の存在チェック。無ければ追加
        self.ready_records()


        # NOTE ［試行シリーズ数］が違うものを１つのファイルに混ぜたくない。ファイルを分けてある


        self._number_of_target = 0        # 処理対象の数
        self._number_of_smalled = 0       # 処理完了の数
        self._number_of_yield = 0         # 処理を途中で譲った数
        self._number_of_passaged = 0      # 空振りで終わったレコード数


        EvenTable.for_each(df=self._df_ev, on_each=self.on_each)

        return is_update_table


    # automatic
    def execute(self):

        self._df_ev = EvenTable.read_df(failure_rate=self._specified_failure_rate, turn_system=self._specified_turn_system, generation_algorythm=self._generation_algorythm, trials_series=self._specified_trials_series)
        #print(self._df_ev)


        self._start_time_for_save = time.time()
        self._is_dirty_csv = False


        # 反復深化探索
        # ===========
        #
        #   ［エラー］が 0 になることを目指していますが、最初から 0 を目指すと、もしかするとエラーは 0 にならなくて、
        #   処理が永遠に終わらないかもしれません。
        #   そこで、［エラー］列は、一気に 0 を目指すのではなく、手前の目標を設定し、その目標を徐々に小さくしていきます。
        #   リミットを指定して、リミットより［エラー］が下回ったら、処理を打ち切ることにします
        #

        speed = 10
        self._current_abs_lower_limit_of_error = ABS_OUT_OF_ERROR
        self._passage_upper_limit = 10

        # ループに最初に１回入るためだけの設定
        worst_abs_best_p_error = ABS_OUT_OF_ERROR

        # １件もデータがない、または
        # 指定の誤差の最小値より、誤差が大きい間繰り返す
        #
        #   NOTE データ件数が０件だと、誤差の最大値が nan になってしまう。データは生成される前提
        #
        while len(self._df_ev) < 1 or self._specified_abs_small_error < worst_abs_best_p_error:
            # ［エラー］列で一番大きい値を取得します
            #
            #   ［調整後の表が出る確率］を 0.5 になるように目指します。［エラー］列は、［調整後の表が出る確率］と 0.5 の差の絶対値です
            #
            best_p_error_min = self._df_ev['best_p_error'].min()
            best_p_error_max = self._df_ev['best_p_error'].max()
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
            is_update_table = self.iteration_deeping()


            #
            # NOTE 小数点以下の桁を長く出しても見づらい
            #
            print(f"[{datetime.datetime.now()}][failure_rate={self._specified_failure_rate}]  update={is_update_table}  target={self._number_of_target}  smalled={self._number_of_smalled}  yield={self._number_of_yield}  passaged={self._number_of_passaged}  {speed=}  worst_error={worst_abs_best_p_error:.7f}(min={best_p_error_min}  max={best_p_error_max})  current_error={self._current_abs_lower_limit_of_error:.7f}  small_error={self._specified_abs_small_error:.7f}  {self._passage_upper_limit=}")


            # 処理が完了したから、ループを抜ける
            if self._number_of_target == self._number_of_smalled:
                print(f"すべてのデータについて、誤差が {self._specified_abs_small_error} 以下になるよう作成完了。 {worst_abs_best_p_error=}")
                break


            # タイムシェアリングのために、処理を譲ることがオーバーヘッドになってきそうなら        
            if 0 < self._number_of_passaged:
                # 初期値が 10 なら 1.1 倍で必ず 1 は増える
                self._passage_upper_limit = int(self._passage_upper_limit * 1.1)

            else:
                self._passage_upper_limit = int(self._passage_upper_limit * 0.9)
                if  self._passage_upper_limit < 10:
                    self._passage_upper_limit = 10

                # タイムシェアリングのために、処理を譲っているというわけでもないとき
                if self._number_of_yield < 1:
                    # スピードがどんどん上がっていく
                    if not is_update_table:
                        speed += 1

                        # 半分、半分でも速そうなので、１０分の９を繰り返す感じで。
                        if self._current_abs_lower_limit_of_error is None:
                            self._current_abs_lower_limit_of_error = worst_abs_best_p_error * 9/speed
                        else:
                            self._current_abs_lower_limit_of_error *= 9/speed
                        
                        if self._current_abs_lower_limit_of_error < self._specified_abs_small_error:
                            self._current_abs_lower_limit_of_error = self._specified_abs_small_error


        print(f"ループから抜けました")


        if self._is_dirty_csv:
            self._is_dirty_csv = False

            # 最後に CSV保存
            print(f"[{datetime.datetime.now()}] 最後に CSV保存 ...")
            EvenTable.to_csv(df=self._df_ev, failure_rate=self._specified_failure_rate, turn_system=self._specified_turn_system, generation_algorythm=self._generation_algorythm, trials_series=self._specified_trials_series)


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


        automation = Automation(
                specified_failure_rate=specified_failure_rate,
                specified_turn_system=specified_turn_system,
                generation_algorythm=generation_algorythm,
                specified_trials_series=specified_trials_series,
                specified_abs_small_error=specified_abs_small_error)
        automation.execute()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
