#
# python step_oa22o0_manual_tpr.py
#
# 手動で［理論的確率の率データ］（TPR）表のスリー・レーツ列を更新します
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, YIELD, TERMINATED, CALCULATION_FAILED, Converter, Specification, ThreeRates
from library.database import TheoreticalProbabilityBestTable, TheoreticalProbabilityTable, TheoreticalProbabilityRatesTable
from library.views import PromptCatalog
from scripts.step_oa22o0_tpr import Automation as StepOa22o0TPR
from config import DEFAULT_UPPER_LIMIT_FAILURE_RATE


# タイムアップ間隔（秒）。タイムシェアリング間隔
INTERVAL_SECONDS = 180

UPPER_LIMIT_UPPER_LIMIT_COINS = 7


def main():
    """関数にすると、return文で処理から途中抜けできるというメリットがある"""

    # ［先後の決め方］を尋ねます
    specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()
    turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)


    # ［将棋の引分け率］を尋ねます
    specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


    # ［将棋の先手勝率］を尋ねます
    specified_p = PromptCatalog.what_is_the_probability_of_flipping_a_coin_and_getting_heads()


    # ［仕様］
    spec = Specification(
            turn_system_id=specified_turn_system_id,
            failure_rate=specified_failure_rate,
            p=specified_p)

    #
    # TODO TP表の theoretical_a_win_rate列、 theoretical_no_win_match_rate列の更新
    #

    # ［理論的確率ベスト］表を読込。無ければナン
    tpb_table, tpb_file_read_result = TheoreticalProbabilityBestTable.from_csv(new_if_it_no_exists=False)

    # ファイルが存在しなければスキップ
    if tpb_table is None:
        print(f"スキップ。［理論的確率ベスト］表が有りません")
    
    else:
        print(f"［理論的確率ベスト］表を読み込んだ")

        # ファイルが存在しなければ無視する。あれば読み込む
        tp_table, tp_file_read_result = TheoreticalProbabilityTable.from_csv(spec=spec, new_if_it_no_exists=False)


        if tp_table is None:
            print(f"スキップ。［理論的確率データ］表が有りません")
        
        else:
            print(f"［理論的確率データ］表を読み込んだ")

            # ファイルが存在しなければ、新規作成する。あれば読み込む
            tpr_table, tpr_file_read_result = TheoreticalProbabilityRatesTable.from_csv(spec=spec, new_if_it_no_exists=True)
            print(f"［理論的確率の率データ］表を読み込んだ")

            automation_oa22o0 = StepOa22o0TPR(
                    seconds_of_time_up=INTERVAL_SECONDS)

            print(f"処理1")

            #
            # FIXME ベスト値更新処理　激重。1分ぐらいかかる重さが何ファイルもある。どうしたもんか？
            #
            calculation_status = automation_oa22o0.update_three_rates_for_a_file_and_save(
                    spec=spec,
                    tp_table=tp_table,
                    tpr_table=tpr_table,

                    #
                    # NOTE upper_limit_coins は、ツリーの深さに直結するから、数字が増えると処理が重くなる
                    # 7 ぐらいから激重。 6ぐらいなら軽い？
                    #
                    upper_limit_upper_limit_coins=UPPER_LIMIT_UPPER_LIMIT_COINS)

            print(f"処理2")

            # 途中の行まで処理したところでタイムアップ
            if calculation_status == YIELD:
                print(f"[{datetime.datetime.now()}] 途中の行まで処理したところでタイムアップ")

            # このファイルは処理失敗した
            elif calculation_status == CALCULATION_FAILED:
                print(f"[{datetime.datetime.now()}] このファイルは処理失敗した")

            # このファイルは処理完了した
            elif calculation_status == TERMINATED:
                print(f"[{datetime.datetime.now()}] このファイルは処理完了した")
            
            else:
                raise ValueError(f"{calculation_status=}")


    print(f"おわり！")

########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """［理論的確率データ］のスリー・レーツ列を更新する
    """

    try:
        main()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
