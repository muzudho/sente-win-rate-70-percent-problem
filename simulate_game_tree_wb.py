#
# 分析
# python simulate_game_tree_wb.py
#
#   GB を GBWB へ変換します
#

import traceback
import pandas as pd
import openpyxl as xl
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.borders import Border, Side

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

        # 変数名の短縮
        ws = self._gt_wb_wrapper.worksheet


        # 列の幅設定
        # width はだいたい 'ＭＳ Ｐゴシック' サイズ11 の半角英文字の個数
        ws.column_dimensions['A'].width = 4
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 14    # 1
        ws.column_dimensions['D'].width = 10
        ws.column_dimensions['E'].width = 14    # 2
        ws.column_dimensions['F'].width = 10
        ws.column_dimensions['G'].width = 14    # 3
        ws.column_dimensions['H'].width = 10
        ws.column_dimensions['I'].width = 14    # 4
        ws.column_dimensions['J'].width = 10
        ws.column_dimensions['K'].width = 14    # 5
        ws.column_dimensions['L'].width = 10
        ws.column_dimensions['M'].width = 14    # 6
        ws.column_dimensions['N'].width = 10


        # 行の高さ設定
        # height の単位はポイント。昔のアメリカ人が椅子に座ってディスプレイを見たとき 1/72 インチに見える大きさが 1ポイント らしいが、そんなんワカラン。目視確認してほしい
        ws.row_dimensions[1].height = 13
        ws.row_dimensions[2].height = 13


        # １行目
        # ------
        # ヘッダー行にする
        row_number = 1

        # インデックス
        column_number = 1
        ws[f'{xl.utils.get_column_letter(column_number)}{row_number}'] = 'no'

        # ２列目～
        for column_number, column_name in enumerate(self._gt_table.df.columns.values, 2):
            ws[f'{xl.utils.get_column_letter(column_number)}{row_number}'] = column_name

        # ２行目
        # ------
        # 空行にする
        row_number = 2


    def on_gt_record(self, row_number, gt_record):

        # 色の参考： 📖 [Excels 56 ColorIndex Colors](https://www.excelsupersite.com/what-are-the-56-colorindex-colors-in-excel/)
        node_bgcolor = PatternFill(patternType='solid', fgColor='FFFFCC')

        # 罫線
        side = Side(style='thick', color='000000')
        # style に入るもの： 'dashDot', 'dashDotDot', 'double', 'hair', 'dotted', 'mediumDashDotDot', 'dashed', 'mediumDashed', 'slantDashDot', 'thick', 'thin', 'medium', 'mediumDashDot'
        upside_node_border = Border(top=side, left=side, right=side)
        downside_node_border = Border(bottom=side, left=side, right=side)


        # 変数名短縮
        ws = self._gt_wb_wrapper.worksheet

        # ３行目～６行目
        # -------------
        # データは３行目から、１かたまり３行を使って描画する
        rn1 = row_number * 3 + 3
        rn2 = row_number * 3 + 3 + 1
        rn3 = row_number * 3 + 3 + 2

        # 行の高さ設定
        # height の単位はポイント。昔のアメリカ人が椅子に座ってディスプレイを見たとき 1/72 インチに見える大きさが 1ポイント らしいが、そんなんワカラン。目視確認してほしい
        ws.row_dimensions[rn1].height = 13
        ws.row_dimensions[rn2].height = 13
        ws.row_dimensions[rn3].height = 6

        ws[f'A{rn1}'].value = gt_record.no
        ws[f'B{rn1}'].value = gt_record.result

        # TODO C列には確率を入れたい
        # TODO D列は空列にしたい
        # TODO E列の上の方の行には 1 を入れたい

        ws[f'F{rn1}'].value = gt_record.e1

        ws[f'G{rn1}'].value = gt_record.n1
        ws[f'G{rn1}'].fill = node_bgcolor
        ws[f'G{rn1}'].border = upside_node_border
        ws[f'G{rn2}'].fill = node_bgcolor
        ws[f'G{rn2}'].border = downside_node_border

        ws[f'H{rn1}'].value = gt_record.e2

        ws[f'I{rn1}'].value = gt_record.n2
        ws[f'I{rn1}'].fill = node_bgcolor
        ws[f'I{rn1}'].border = upside_node_border
        ws[f'I{rn2}'].fill = node_bgcolor
        ws[f'I{rn2}'].border = downside_node_border

        ws[f'J{rn1}'].value = gt_record.e3

        ws[f'K{rn1}'].value = gt_record.n3
        ws[f'K{rn1}'].fill = node_bgcolor
        ws[f'K{rn1}'].border = upside_node_border
        ws[f'K{rn2}'].fill = node_bgcolor
        ws[f'K{rn2}'].border = downside_node_border

        ws[f'L{rn1}'].value = gt_record.e4

        ws[f'M{rn1}'].value = gt_record.n4
        ws[f'M{rn1}'].fill = node_bgcolor
        ws[f'M{rn1}'].border = upside_node_border
        ws[f'M{rn2}'].fill = node_bgcolor
        ws[f'M{rn2}'].border = downside_node_border

        ws[f'N{rn1}'].value = gt_record.e5

        ws[f'O{rn1}'].value = gt_record.n5
        ws[f'O{rn1}'].fill = node_bgcolor
        ws[f'O{rn1}'].border = upside_node_border
        ws[f'O{rn2}'].fill = node_bgcolor
        ws[f'O{rn2}'].border = downside_node_border

        ws[f'P{rn1}'].value = gt_record.e6

        ws[f'Q{rn1}'].value = gt_record.n6
        ws[f'Q{rn1}'].fill = node_bgcolor
        ws[f'Q{rn1}'].border = upside_node_border
        ws[f'Q{rn2}'].fill = node_bgcolor
        ws[f'Q{rn2}'].border = downside_node_border

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
