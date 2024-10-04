#
# ロギング
#
import datetime

from library.file_paths import get_automatic_no1_log_file_path


class AutomaticNo1Logging():


    _log_file_path = None


    @classmethod
    def log_progress(clazz, self, failure_rate, shall_print=False):
        progress = f"[{datetime.datetime.now()}] {failure_rate=}"

        if shall_print:
            print(progress)

        if clazz._log_file_path is None:
            clazz._log_file_path = get_automatic_no1_log_file_path()
        
        with open(clazz._log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{progress}\n")
