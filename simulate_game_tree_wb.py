#
# 分析
# python simulate_game_tree_wb.py
#
#   GB を GBWB へ変換します
#

import traceback
import pandas as pd
import openpyxl as xl

from library import HEAD, TAIL, ALICE, IN_GAME, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths
from library.database import GameTreeRecord, GameTreeTable
from library.workbooks import GameTreeWorkbookWrapper
from library.views import stringify_csv_of_score_board_view_body, PromptCatalog
from library.score_board import search_all_score_boards
from library.views import ScoreBoardViewData
from scripts import SaveOrIgnore


########################################
# コマンドから実行時
########################################


class Automation():


    def __init__(self, gt_table, gt_wb_wrapper):
        self._gt_table = gt_table
        self._gt_wb_wrapper = gt_wb_wrapper


    def on_header(self):
        row_number = 1

        # インデックス
        column_number = 1
        self._gt_wb_wrapper.worksheet[f'{xl.utils.get_column_letter(column_number)}{row_number}'] = 'no'

        # ２列目～
        for column_number, column_name in enumerate(self._gt_table.df.columns.values, 2):
            self._gt_wb_wrapper.worksheet[f'{xl.utils.get_column_letter(column_number)}{row_number}'] = column_name


    def on_gt_record(self, row_number, gt_record):

        # 変数名短縮
        WS = self._gt_wb_wrapper.worksheet

        # データは２行目から
        RN = row_number + 2

        WS[f'A{RN}'].value = gt_record.no
        WS[f'B{RN}'].value = gt_record.result
        WS[f'C{RN}'].value = gt_record.e1
        WS[f'D{RN}'].value = gt_record.n1
        WS[f'E{RN}'].value = gt_record.e2
        WS[f'F{RN}'].value = gt_record.n2
        WS[f'G{RN}'].value = gt_record.e3
        WS[f'H{RN}'].value = gt_record.n3
        WS[f'I{RN}'].value = gt_record.e4
        WS[f'J{RN}'].value = gt_record.n4
        WS[f'K{RN}'].value = gt_record.e5
        WS[f'L{RN}'].value = gt_record.n5
        WS[f'M{RN}'].value = gt_record.e6
        WS[f'N{RN}'].value = gt_record.n6

        # TODO GT テーブルの内容を GTWB のシートへコピー、スタイルも設定


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


        # GTテーブル
        gt_table, gt_file_read_result = GameTreeTable.from_csv(
                spec=spec,
                span=specified_series_rule.step_table.span,
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                new_if_it_no_exists=False)

        if gt_file_read_result.is_file_not_found:
            raise ValueError(f"GTファイルが見つかりません {gt_file_read_result.file_path=}")


        # GTWB ファイル作成
        # オリジナルはインターフェースに癖があるので、ラッパーを作成してそれを使う
        gt_wb_wrapper = GameTreeWorkbookWrapper.instantiate(
                spec=spec,
                span=specified_series_rule.step_table.span,
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD))

        # ワークブックを開く（既存なら削除してから新規作成）
        gt_wb = gt_wb_wrapper.open_workbook(remove_workbook_if_it_exists=True)

        # GameTree シートを作成
        gt_wb_wrapper.create_sheet('GameTree', shall_overwrite=False)

        # 既存の Sheet シートを削除
        gt_wb_wrapper.remove_sheet('Sheet')

        automation = Automation(gt_table=gt_table, gt_wb_wrapper=gt_wb_wrapper)

        # GTWB の Sheet シートへのヘッダー書出し
        automation.on_header()

        # GTWB の Sheet シートへの各行書出し
        gt_table.for_each(automation.on_gt_record)

        # GTWB ファイルの保存
        gt_wb_wrapper.save()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
