#
# python step_oa21o0_manual_tp.py
#
# 手動で［理論的確率データ］（TP）表に新規行を挿入します
#

import traceback
import datetime

from library import Converter, Specification
from library.file_paths import TheoreticalProbabilityFilePaths
from library.database import TheoreticalProbabilityBestTable, TheoreticalProbabilityTable
from library.views import PromptCatalog
from scripts import SaveOrIgnore
from scripts.step_oa21o0_tp import GeneratorOfTP


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """［理論的確率データ］のスリー・レーツ列を更新する

    TODO TPR表の expected_a_victory_rate_by_duet 列、 expected_no_win_match_rate列の更新
    """

    try:
        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()
        turn_system_name = Converter.turn_system_id_to_name(specified_turn_system_id)


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        # ［将棋の先手勝率］を尋ねます
        specified_p = PromptCatalog.what_is_the_probability_of_flipping_a_coin_and_getting_heads()


        # ［探索の深さ］を尋ねます
        specified_depth = PromptCatalog.how_many_depth_in_search()


        # ［仕様］
        spec = Specification(
                turn_system_id=specified_turn_system_id,
                failure_rate=specified_failure_rate,
                p=specified_p)
            

        #
        # FIXME 飛び番で挿入されてる？ ----> 既存行を、最新行で上書きされてるのでは？
        #
        print(f"[{datetime.datetime.now()}] step o5o0 insert new record in tp...")
        generator_of_tp = GeneratorOfTP(depth=specified_depth)

        # まず、［理論的確率データ］ファイルに span, t_step, h_step のインデックスを持った仮行をある程度の数、追加していく。このとき、スリー・レーツ列は入れず、空けておく
        number_of_dirty = generator_of_tp.execute_by_spec(spec=spec)


        # ［理論的確率データ］（TP）ファイル保存
        if 0 < number_of_dirty:
            successful, target_file_path = SaveOrIgnore.execute(
                    log_file_path=TheoreticalProbabilityFilePaths.as_log(spec=spec),
                    on_save_and_get_file_name=tp_table.to_csv)
            
            if successful:
                print(f"[{datetime.datetime.now()}] SAVED dirty={number_of_dirty} file={target_file_path}")


        print(f"おわり！")


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
