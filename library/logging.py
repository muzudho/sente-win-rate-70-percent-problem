#
# ロギング
#
import datetime

from library.file_paths import StepO1o0AutomaticFilePaths


class StepO1o0AutomaticLogging():


    _log_file_path = None


    @classmethod
    def log_progress(clazz, failure_rate, shall_print=False):
        progress = f"[{datetime.datetime.now()}] {failure_rate=}"

        if shall_print:
            print(progress)

        if clazz._log_file_path is None:
            clazz._log_file_path = StepO1o0AutomaticFilePaths.as_log()
        
        with open(clazz._log_file_path, 'a', encoding='utf8') as f:
            f.write(f"{progress}\n")
