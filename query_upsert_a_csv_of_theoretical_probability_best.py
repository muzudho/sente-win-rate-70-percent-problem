#
# 分析
# python query_upsert_a_csv_of_theoretical_probability_best.py
#
#   ［仕様］［シリーズ・ルール］について、５分５分に近いものをピックアップします
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, UPPER_LIMIT_FAILURE_RATE, Converter, Specification, ThreeRates
from library.database import TheoreticalProbabilityTable, TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable
from scripts.upsert_a_csv_of_theoretical_probability_best import AutomationOne as UpsertCsvOfTheoreticalProbabilityBestOne



########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［将棋の先手勝率］を尋ねます
        prompt = f"""\

Example: 70% is 0.7
What is the probability of flipping a coin and getting heads? """
        specified_p = float(input(prompt))


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
            specified_turn_system_id = FROZEN_TURN
        elif choice == '2':
            specified_turn_system_id = ALTERNATING_TURN
        else:
            raise ValueError(f"{choice=}")

        turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)


        # ［仕様］
        spec = Specification(
                p=specified_p,
                failure_rate=specified_failure_rate,
                turn_system_id=specified_turn_system_id)


        # ［理論的確率ベストデータ］新規作成または更新
        upsert_csv_of_theoretical_probability_best_one = UpsertCsvOfTheoreticalProbabilityBestOne(spec=spec)

        # FIXME
        is_dirty, df_best = upsert_csv_of_theoretical_probability_best_one.execute_one()

        # FIXME ベスト値更新処理　激重。1分ぐらいかかる重さが何ファイルもある。どうしたもんか？
        # FIXME span, t_step, h_step は主キーでは無いのでは？
        # ファイルに変更があれば、CSVファイル保存
        if is_dirty:
            csv_file_path_to_wrote = TheoreticalProbabilityBestTable.to_csv(df=df_best)
            print(f"[{datetime.datetime.now()}][turn_system_name={turn_system_name}  failure_rate={spec.failure_rate * 100:.1f}%  p={spec.p * 100:.1f}] write theoretical probability best to `{csv_file_path_to_wrote}` file ...")


        print(f"おわり！")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
