#
# 汎用スクリプト
#
import time
import random

from library.logging import Logging


class SaveWithRetry():
    """リトライ付き保存"""
    

    @staticmethod
    def execute(file_path, on_save_and_get_file_name):
        """実行

        Parameters
        ----------
        file_path : str
            保存するファイルへのパス
        on_save_and_get_csv_file_name : func
            ファイルへ保存し、そのファイル名を返す関数
        """
        while True:
            try:
                file_path = on_save_and_get_file_name()

                # ロギング
                Logging.notice_log(
                        file_path=file_path,
                        message=f"save to `{file_path}` file...",
                        shall_print=True)
                break

            except PermissionError as e:
                # ファイルを開いて作業中かもしれない。しばらく待ってリトライする
                wait_for_seconds = random.randint(30, 15*60)

                # ロギング
                Logging.notice_log(
                        file_path=file_path,
                        # ファイルパスは例外メッセージの方に含まれている
                        message=f"save file to failed. wait for {wait_for_seconds} seconds and retry. {e}",
                        shall_print=True)

                time.sleep(wait_for_seconds)