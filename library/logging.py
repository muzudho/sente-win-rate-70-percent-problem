#
# ロギング
#
import datetime

from library.file_paths import StepO1o0AutomaticFilePaths


class Logging():
    """ロギング"""


    @staticmethod
    def notice_log(file_path, message, shall_print=False):
        text = f"[{datetime.datetime.now()}] NOTICE {message}"

        if shall_print:
            print(text)

        if clazz._log_file_path is None:
            clazz._log_file_path = StepO1o0AutomaticFilePaths.as_log()
        
        with open(file_path, 'a', encoding='utf8') as f:
            f.write(f"{text}\n")
