#
# python step_oa23o0_manual_upsert_record_in_tpb.py
#
#   手動で［理論的確率ベスト］（TPB）CSVファイルへアップサートします。
#   ［仕様］［シリーズ・ルール］について、５分５分に近いものをピックアップします
#

import traceback
import datetime

from library import FROZEN_TURN, ALTERNATING_TURN, EVEN, ABS_OUT_OF_ERROR, Converter, Specification, ThreeRates
from library.file_paths import TheoreticalProbabilityBestFilePaths
from library.database import TheoreticalProbabilityBestRecord, TheoreticalProbabilityBestTable
from library.views import PromptCatalog
from scripts import SaveWithRetry
from scripts.step_oa23o0_upsert_record_in_tpb import GeneratorOneOfTPB



########################################
# コマンドから実行時
########################################

if __name__ == '__main__':
    """Step O2o3o0 ［理論的確率ベスト］表の新規作成または更新

    TODO 先に TPR表の expected_a_victory_rate_by_duet 列、 expected_no_win_match_rate列が更新されている必要があります    
    """

    try:
        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()
        turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        # ［将棋の先手勝率］を尋ねます
        specified_p = PromptCatalog.what_is_the_probability_of_flipping_a_coin_and_getting_heads()


        # ［理論的確率ベスト］表を読込。無ければナン
        tpb_table, tpb_file_read_result = TheoreticalProbabilityBestTable.from_csv(new_if_it_no_exists=False)

        # ファイルが存在しなければスキップ
        if tpb_table==None:
            print(f"［理論的確率ベスト］表が有りません")
        
        else:
            generator_one_of_tpb = GeneratorOneOfTPB(tpb_table=tpb_table)

            # ［仕様］
            spec = Specification(
                    turn_system_id=specified_turn_system_id,
                    failure_rate=specified_failure_rate,
                    p=specified_p)

            #
            # FIXME ベスト値更新処理　激重。1分ぐらいかかる重さが何ファイルもある。どうしたもんか？
            #
            is_dirty, is_file_not_found = generator_one_of_tpb.execute_a_spec(spec=spec)

            if is_file_not_found:
                print("ファイルが見つかりません(B)")
            
            # ファイルに変更があれば、CSVファイル保存
            elif is_dirty:
                SaveWithRetry.execute(
                        log_file_path=TheoreticalProbabilityBestFilePaths.as_log(),
                        on_save_and_get_file_name=TheoreticalProbabilityBestTable.to_csv)


        print(f"おわり！")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
