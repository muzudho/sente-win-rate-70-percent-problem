#
# 分析
# python step_oa21o0_automatic_tp.py
#
#   ［理論的確率データ］（TP）表を作成します。
#   １シリーズのコインの出目について、全パターン網羅した表を作成します
#

import traceback

from config import DEFAULT_MAX_DEPTH
from scripts import ForEachSpec
from scripts.step_o5o0_insert_new_record_in_tp import Automation as StepO5o0InsertNewRecordInTp


########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # TODO 自動調整のいい方法が思い浮かばない
        # とりあえず、 depth が どんどん増えていくものとする。
        for depth in range(1, DEFAULT_MAX_DEPTH):

            automation = StepO5o0InsertNewRecordInTp(depth=depth)

            ForEachSpec.execute(on_each_spec=automation.execute_by_spec)


        # 現実的に、完了しない想定
        print("完了")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
