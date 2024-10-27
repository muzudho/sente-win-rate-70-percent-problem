import time
import datetime

from library import HEAD, TAIL, ALICE, SUCCESSFUL, FAILED, Converter, judge_series, LargeSeriesTrialSummary, SequenceOfFaceOfCoin, Candidate
from library.database import EmpiricalProbabilityDuringTrialsRecord
from library.file_paths import EmpiricalProbabilityDuringTrialsFilePaths
from library.views import DebugWrite


class SeriesRuleCursor():

    def __init__(self, p, p_error, series_rule):
        self._p = p
        self._p_error = p_error
        self._series_rule = series_rule


    @property
    def p(self):
        return self._p


    @property
    def p_error(self):
        return self._p_error


    @property
    def series_rule(self):
        return self._series_rule


class SearchRecordOfEDPT():
    """自動化
    
    NOTE 探索の打切り判定の制御は、コールバック関数を使って呼び出し元でやるようにします
    """


    def __init__(self, specified_trial_series, specified_turn_system_id, specified_failure_rate, on_callback):
        self._specified_trial_series = specified_trial_series
        self._specified_turn_system_id = specified_turn_system_id
        self._specified_failure_rate = specified_failure_rate
        self._on_callback = on_callback


        self._start_time_for_save = None    # CSV保存用タイマー


        self._best_series_rule_cursor = None
        self._latest_series_rule_cursor = None
        self._candidate_history_text = None # 候補の履歴

        self._is_passaged = False     # 処理はしたが、更新はなかった
        self._is_dirty_record = False  # レコードの更新があって、保存してない
        self._is_cutoff = False   # FIXME 打ち切りフラグ。本当はタイムシェアリング書くべき


    @property
    def specified_trial_series(self):
        return self._specified_trial_series


    @property
    def specified_turn_system_id(self):
        return self._specified_turn_system_id


    @property
    def specified_failure_rate(self):
        return self._specified_failure_rate


    @property
    def best_series_rule_cursor(self):
        return self._best_series_rule_cursor


    @property
    def latest_series_rule_cursor(self):
        return self._latest_series_rule_cursor


    @property
    def candidate_history_text(self):
        return self._candidate_history_text


    @property
    def is_passaged(self):
        """処理はしたが、更新はなかった"""
        return self._is_passaged


    @property
    def is_dirty_record(self):
        """レコードの更新があって、保存してない"""
        return self._is_dirty_record


    @property
    def is_cutoff(self):
        """探索打切りか？"""
        return self._is_cutoff


    def execute(self, series_rule):

        # 力任せ探索
        list_of_trial_results_for_one_series = []

        for i in range(0, self._specified_trial_series):

            # １シリーズをフルに対局したときのコイントスした結果の疑似リストを生成
            path_of_face_of_coin = SequenceOfFaceOfCoin.make_sequence_of_playout(
                    spec=series_rule.spec,
                    upper_limit_coins=series_rule.upper_limit_coins)

            # FIXME 検証
            if len(path_of_face_of_coin) < series_rule.shortest_coins:
                text = f"{spec.p=} 指定の対局シートの長さ {len(path_of_face_of_coin)} は、最短対局数の理論値 {series_rule.shortest_coins} を下回っています。このような対局シートを指定してはいけません"
                print(f"""{text}
{path_of_face_of_coin=}
{series_rule.upper_limit_coins=}
""")
                raise ValueError(text)


            # 疑似のリストをもとに、シリーズとして見てみる
            trial_results_for_one_series = judge_series(
                    spec=series_rule.spec,
                    series_rule=series_rule,
                    path_of_face_of_coin=path_of_face_of_coin)
            
            list_of_trial_results_for_one_series.append(trial_results_for_one_series)


        # シミュレーションの結果
        large_series_trial_summary = LargeSeriesTrialSummary(
                specified_trial_series=self._specified_trial_series,
                list_of_trial_results_for_one_series=list_of_trial_results_for_one_series)


        # この［シリーズ・ルール］でのシミュレーション結果（今回の候補）
        # Ａさんが勝った回数
        s_wins_a = large_series_trial_summary.wins(challenged=SUCCESSFUL, winner=ALICE)
        f_wins_a = large_series_trial_summary.wins(challenged=FAILED, winner=ALICE)
        temp_p = (s_wins_a + f_wins_a) / self._specified_trial_series
        self._latest_series_rule_cursor = SeriesRuleCursor(
                p=temp_p,
                p_error=temp_p - 0.5,
                series_rule=series_rule)


        # アップデート
        is_update = self._best_series_rule_cursor is None or abs(self._latest_series_rule_cursor.p_error) < abs(self._best_series_rule_cursor.p_error)
        if is_update:
            self._best_series_rule_cursor = SeriesRuleCursor(
                    p=self._latest_series_rule_cursor.p,
                    p_error=self._latest_series_rule_cursor.p_error,
                    series_rule=self._latest_series_rule_cursor.series_rule)

            # ［シリーズ・ルール候補］
            candidate_obj = Candidate(
                    p_error=self._best_series_rule_cursor.p_error,
                    trial_series=self._specified_trial_series,
                    h_step=self._best_series_rule_cursor.series_rule.step_table.get_step_by(face_of_coin=HEAD),   # FIXME FAILED の方は記録しなくていい？
                    t_step=self._best_series_rule_cursor.series_rule.step_table.get_step_by(face_of_coin=TAIL),
                    span=self._best_series_rule_cursor.series_rule.step_table.span,
                    shortest_coins=self._best_series_rule_cursor.series_rule.shortest_coins,             # ［最短対局数］
                    upper_limit_coins=self._best_series_rule_cursor.series_rule.upper_limit_coins)       # ［上限対局数］
            candidate_str = candidate_obj.as_str()
            turn_system_name = Converter.turn_system_id_to_name(self._specified_turn_system_id)
            print(f"{DebugWrite.stringify(trial_series=self._specified_trial_series, turn_system_name=turn_system_name, failure_rate=self._specified_failure_rate, p=series_rule.spec.p)}{candidate_str}", flush=True) # すぐ表示

            # ［シリーズ・ルール候補］列を更新
            #
            #   途中の計算式。半角空裏区切り
            #
            if isinstance(self._candidate_history_text, str):
                self._candidate_history_text = f"{self._candidate_history_text} {candidate_str}"
            else:
                self._candidate_history_text = candidate_str


        is_break = self._on_callback(context=self, is_update=is_update)
        return is_break
