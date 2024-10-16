#
# 分析
# python simulate_game_tree.py
#
#   １シリーズのコインの出目について、全パターン網羅した樹形図をCSV形式で出力します。
#   レコードは可変列です
#

import traceback
import pandas as pd

from library import HEAD, TAIL, ALICE, IN_GAME, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths
from library.database import GameTreeNode, GameTreeRecord, GameTreeTable
from library.views import stringify_csv_of_score_board_view_body, PromptCatalog
from library.score_board import search_all_score_boards
from library.views import ScoreBoardViewData
from scripts import SaveOrIgnore


class Automatic():


    def __init__(self, spec, gt_table):
        self._spec = spec
        self._gt_table = gt_table


    def on_score_board_created(self, score_board):


        no = score_board.pattern_no


        if score_board.game_results == IN_GAME:
            raise ValueError(f"対局中なのはおかしい")
        
        elif score_board.game_results == ALICE_FULLY_WON:
            result = "達成でＡさんの勝ち"

        elif score_board.game_results == BOB_FULLY_WON:
            result = "達成でＢさんの勝ち"

        elif score_board.game_results == ALICE_POINTS_WON:
            result = "勝ち点差でＡさんの勝ち"

        elif score_board.game_results == BOB_POINTS_WON:
            result = "勝ち点差でＢさんの勝ち"
        
        elif score_board.game_results == NO_WIN_MATCH:
            result = "勝者なし"

        else:
            raise ValueError(f"{score_board.game_results=}")
        


        # score board view data
        V = ScoreBoardViewData.from_data(score_board)

        a_span = int(V.path_of_a_count_down_points_str[1])
        b_span = int(V.path_of_b_count_down_points_str[1])
        a_pts = a_span
        b_pts = b_span

        # [0], [1] は見出しデータ
        MIDASI = 2
        number_of_round = len(V.path_of_round_number_str) - MIDASI

        face_list = []
        winner_list = []
        pts_list = []
        rate_list = []

        pattern_rate = 1
        successful_p = (1 - self._spec.failure_rate) * self._spec.p
        successful_q = (1 - self._spec.failure_rate) * (1 - self._spec.p)

        for i in range(0, number_of_round):
            prev_a_pts = int(V.path_of_a_count_down_points_str[i + MIDASI - 1])
            prev_b_pts = int(V.path_of_b_count_down_points_str[i + MIDASI - 1])
            a_pts = int(V.path_of_a_count_down_points_str[i + MIDASI])
            b_pts = int(V.path_of_b_count_down_points_str[i + MIDASI])


            # FIXME どちらが勝ったかの判定は、カウントが減っているかで判定
            if a_pts < prev_a_pts and b_pts < prev_b_pts:
                raise ValueError(f'両者のポイントが変わっているのはおかしい  {prev_a_pts=}  {prev_b_pts=}  {a_pts=}  {b_pts=}')
            elif a_pts < prev_a_pts:
                player_name = 'A'
            elif b_pts < prev_b_pts:
                player_name = 'B'
            else:
                player_name = '失'


            face_of_coin = V.path_of_face_of_coin_str[i + MIDASI]


            # ［失敗］表記
            if player_name == '失':
                winner_list.append('N')
                pts_list.append(-1)

            else:
                # カウントダウン式で記録されているので、カウントアップ式に変換する
                if player_name == 'A':
                    pts = a_span - a_pts
                elif player_name == 'B':
                    pts = b_span - b_pts
                else:
                    raise ValueError(f'{player_name=}')

                winner_list.append(player_name)
                pts_list.append(pts)


            # 確率計算
            if face_of_coin == '表':
                face_list.append('h')
                pattern_rate *= successful_p
            elif face_of_coin == '裏':
                face_list.append('t')
                pattern_rate *= successful_q
            elif player_name == '失':
                face_list.append('f')
                pattern_rate *= self._spec.failure_rate
            else:
                raise ValueError(f'{player_name=}')


            rate_list.append(pattern_rate)


        node_list = []

        if 0 < number_of_round:
            i = 0
            node_list.append(GameTreeNode(face=face_list[i], winner=winner_list[i], pts=pts_list[i], rate=rate_list[i]))
        else:
            node_list.append(GameTreeNode(face=None, winner=None, pts=None, rate=None))

        if 1 < number_of_round:
            i = 1
            node_list.append(GameTreeNode(face=face_list[i], winner=winner_list[i], pts=pts_list[i], rate=rate_list[i]))
        else:
            node_list.append(GameTreeNode(face=None, winner=None, pts=None, rate=None))

        if 2 < number_of_round:
            i = 2
            node_list.append(GameTreeNode(face=face_list[i], winner=winner_list[i], pts=pts_list[i], rate=rate_list[i]))
        else:
            node_list.append(GameTreeNode(face=None, winner=None, pts=None, rate=None))

        if 3 < number_of_round:
            i = 3
            node_list.append(GameTreeNode(face=face_list[i], winner=winner_list[i], pts=pts_list[i], rate=rate_list[i]))
        else:
            node_list.append(GameTreeNode(face=None, winner=None, pts=None, rate=None))

        if 4 < number_of_round:
            i = 4
            node_list.append(GameTreeNode(face=face_list[i], winner=winner_list[i], pts=pts_list[i], rate=rate_list[i]))
        else:
            node_list.append(GameTreeNode(face=None, winner=None, pts=None, rate=None))

        if 5 < number_of_round:
            i = 5
            node_list.append(GameTreeNode(face=face_list[i], winner=winner_list[i], pts=pts_list[i], rate=rate_list[i]))
        else:
            node_list.append(GameTreeNode(face=None, winner=None, pts=None, rate=None))


        gt_table.upsert_record(
                welcome_record=GameTreeRecord(
                        no=no,
                        result=result,
                        node_list=node_list))


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        # ［先後の決め方］を尋ねます
        specified_turn_system_id = PromptCatalog.which_method_do_you_use_to_determine_sente_and_gote()


        # ［将棋の引分け率］を尋ねます
        specified_failure_rate = PromptCatalog.what_is_the_failure_rate()


        # ［将棋の先手勝率］を尋ねます
        specified_p = PromptCatalog.what_is_the_probability_of_flipping_a_coin_and_getting_heads()


        # ［目標の点数］を尋ねます
        specified_span = PromptCatalog.how_many_goal_win_points()


        # ［後手で勝ったときの勝ち点］を尋ねます
        specified_t_step = PromptCatalog.how_many_win_points_of_tail_of_coin()


        # ［先手で勝ったときの勝ち点］を尋ねます
        specified_h_step = PromptCatalog.how_many_win_points_of_head_of_coin()


        # ［仕様］
        spec = Specification(
                turn_system_id=specified_turn_system_id,
                failure_rate=specified_failure_rate,
                p=specified_p)

        # FIXME 便宜的に［試行シリーズ数］は 1 固定
        specified_trial_series = 1

        # ［シリーズ・ルール］。任意に指定します
        specified_series_rule = SeriesRule.make_series_rule_base(
                spec=spec,
                span=specified_span,
                t_step=specified_t_step,
                h_step=specified_h_step)


        # GTテーブル。ファイルが無ければ作成します
        gt_table, file_read_result = GameTreeTable.from_csv(
                spec=spec,
                span=specified_series_rule.step_table.span,
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                new_if_it_no_exists=True)
        

        automatic = Automatic(spec=spec, gt_table=gt_table)

        three_rates, all_patterns_p = search_all_score_boards(
                series_rule=specified_series_rule,
                on_score_board_created=automatic.on_score_board_created)


        # CSVファイル出力（追記）
        SaveOrIgnore.execute(
                log_file_path=GameTreeFilePaths.as_log(
                        spec=spec,
                        span=specified_series_rule.step_table.span,
                        t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                        h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD)),
                on_save_and_get_file_name=gt_table.to_csv)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
