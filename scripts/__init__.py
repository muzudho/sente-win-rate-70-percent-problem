#
# 汎用スクリプト
#
import time
import random
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, Converter, Specification, SeriesRule
from library.logging import Logging
from config import DEFAULT_UPPER_LIMIT_FAILURE_RATE


class SaveOrIgnore():
    """保存、ただし保存できなかったら変更を破棄して続行"""
    

    @staticmethod
    def execute(log_file_path, on_save_and_get_file_name):
        """実行

        Parameters
        ----------
        log_file_path : str
            保存するファイルへのパス
        on_save_and_get_file_name : func
            ファイルへ保存し、そのファイル名を返す関数
        
        Returns
        -------
        successful : bool
            保存に成功したか？
        target_file_path : str
            保存した対象ファイル（ログファイルではない）へのパス。保存できなかった場合、ナン
        """
        try:
            target_file_path = on_save_and_get_file_name()

            # ロギング
            Logging.notice_log(
                    file_path=log_file_path,
                    message=f"save to `{target_file_path}` file...",
                    shall_print=True)

            return True, target_file_path


        except PermissionError as e:
            # ロギング
            Logging.notice_log(
                    file_path=log_file_path,
                    # ファイルパスは例外メッセージの方に含まれている
                    message=f"save file to failed. ignored. {e}",
                    shall_print=True)

            return False, None


class SaveWithRetry():
    """リトライ付き保存"""
    

    @staticmethod
    def execute(log_file_path, on_save_and_get_file_name):
        """実行

        Parameters
        ----------
        log_file_path : str
            ログ・ファイルへのパス
        on_save_and_get_file_name : func
            ファイルへ保存し、そのファイル名を返す関数
        """
        while True:
            try:
                target_file_path = on_save_and_get_file_name()

                # ロギング
                Logging.notice_log(
                        file_path=log_file_path,
                        message=f"save to `{target_file_path}` file...",
                        shall_print=True)
                break

            # ファイルを開いて作業中かもしれない。しばらく待ってリトライする
            except PermissionError as e:

                # ロギング
                Logging.notice_log(
                        file_path=log_file_path,
                        # ファイルパスは例外メッセージの方に含まれている
                        message=f"save file to failed. {e}",
                        shall_print=True)

                IntervalForRetry.sleep(shall_print=True)


class ForEachTsFr():


    @staticmethod
    def execute(on_each_tsfr):
        """
        Parameters
        ----------
        on_each_tsfr : func
            関数
        """

        # ［先後の決め方］
        for turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(DEFAULT_UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
                failure_rate = failure_rate_percent / 100
                    
                on_each_tsfr(turn_system_id=turn_system_id, failure_rate=failure_rate)


class ForEachFr():


    @staticmethod
    def execute(on_each_fr):
        """
        Parameters
        ----------
        on_each_fr : func
            関数
        """

        # ［将棋の引分け率］
        for failure_rate_percent in range(0, int(DEFAULT_UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
            failure_rate = failure_rate_percent / 100
                
            on_each_fr(failure_rate=failure_rate)


class ForEachSpec():


    @staticmethod
    def execute(on_each_spec):
        """
        Parameters
        ----------
        on_each_spec : func
            関数
        """

        # ［先後の決め方］
        for turn_system_id in [ALTERNATING_TURN, FROZEN_TURN]:

            # ［将棋の引分け率］
            for failure_rate_percent in range(0, int(DEFAULT_UPPER_LIMIT_FAILURE_RATE * 100) + 1, 5): # 5％刻み。 100%は除く。0除算が発生するので
                failure_rate = failure_rate_percent / 100

                # ［将棋の先手勝率］
                for p_percent in range(50, 96):
                    p = p_percent / 100

                    # 仕様
                    spec = Specification(
                            turn_system_id=turn_system_id,
                            failure_rate=failure_rate,
                            p=p)
                    
                    on_each_spec(spec=spec)


class ForEachSeriesRule():


    @staticmethod
    def execute(spec, start_span, start_t_step, start_h_step, end_span, on_each):
        """実行

        ［目標の点数］、［裏番で勝ったときの勝ち点］、［表番で勝ったときの勝ち点］を１つずつ進めていく探索です。
        ［目標の点数］＞＝［裏番で勝ったときの勝ち点］＞＝［表番で勝ったときの勝ち点］という関係があります。

        Parameters
        ----------
        spec : Specification
            ［仕様］
        start_span : int
            ［目標の点数］の開始値
        start_t_step : int
            ［裏番で勝ったときの勝ち点］の開始値
        start_h_step : int
            ［表番で勝ったときの勝ち点］の開始値
        end_span : int
            ［目標の点数］の終了値。この数を含まない
        on_each : func
            コールバック関数
        """

        span = start_span
        t_step = start_t_step
        h_step = start_h_step

        while span < end_span:

            # ［シリーズ・ルール］
            series_rule = SeriesRule.make_series_rule_base(
                    spec=spec,
                    span=span,
                    t_step=t_step,
                    h_step=h_step)

            is_break = on_each(series_rule)

            if is_break:
                break

            span, t_step, h_step = ForEachSeriesRule.increase(
                    span=span,
                    t_step=t_step,
                    h_step=h_step)


    @staticmethod
    def increase(span, t_step, h_step):
        """カウントアップ"""
        h_step += 1
        if t_step < h_step:
            h_step = 1
            t_step += 1
            if span < t_step:
                t_step = 1
                span += 1

        return span, t_step, h_step


    @staticmethod
    def assert_sth(span, t_step, h_step):
        if t_step < h_step:
            raise ValueError(f"［コインの表が出たときの勝ち点］{h_step=} が、［コインの裏が出たときの勝ち点］ {t_step=} を上回るのはおかしいです {span=}")

        if span < t_step:
            raise ValueError(f"［コインの裏が出たときの勝ち点］{t_step=} が、［目標の点数］{span=} を上回るのはおかしいです {h_step=}")


class IntervalForRetry():
    """リトライのためのインターバル"""


    def sleep(min_secs=30, max_secs=900, shall_print=False):

        wait_for_seconds = random.randint(min_secs, max_secs)

        if shall_print:
            print(f"[{datetime.datetime.now()}] wait for {wait_for_seconds} seconds and retry.")

        time.sleep(wait_for_seconds)
