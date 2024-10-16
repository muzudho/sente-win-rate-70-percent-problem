#
# 分析
# python simulate_game_tree_wb.py
#
#   GB を GBWB へ変換します
#

import traceback
import datetime
import pandas as pd
import openpyxl as xl
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.borders import Border, Side

from library import HEAD, TAIL, ALICE, IN_GAME, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH, Specification, SeriesRule
from library.file_paths import GameTreeFilePaths
from library.database import GameTreeNode, GameTreeRecord, GameTreeTable
from library.workbooks import GameTreeWorkbookWrapper
from library.views import stringify_csv_of_score_board_view_body, PromptCatalog
from library.score_board import search_all_score_boards
from library.views import ScoreBoardViewData
from library.game_tree_view import GameTreeView
from scripts import SaveOrIgnore


class Automation():


    def __init__(self, gt_table, gt_wb_wrapper):
        self._gt_table = gt_table
        self._gt_wb_wrapper = gt_wb_wrapper
        self._prev_gt_record = GameTreeRecord.new_empty()
        self._curr_gt_record = GameTreeRecord.new_empty()
        self._next_gt_record = GameTreeRecord.new_empty()


    def forward_cursor(self, next_gt_record):
        # 送り出し
        self._prev_gt_record = self._curr_gt_record
        self._curr_gt_record = self._next_gt_record
        self._next_gt_record = next_gt_record


    def on_header(self):

        # 変数名の短縮
        ws = self._gt_wb_wrapper.worksheet


        # 列の幅設定
        # width はだいたい 'ＭＳ Ｐゴシック' サイズ11 の半角英文字の個数

        # TODO C列には確率を入れたい
        # TODO D列は空列にしたい
        # TODO E列の上の方の行には 1 を入れたい

        ws.column_dimensions['A'].width = 4     # no
        ws.column_dimensions['B'].width = 20    # result
        ws.column_dimensions['C'].width = 14    # rate
        ws.column_dimensions['D'].width = 14    # empty column
        ws.column_dimensions['E'].width = 14    # root node
        ws.column_dimensions['F'].width = 2    # 1
        ws.column_dimensions['G'].width = 14
        ws.column_dimensions['H'].width = 10
        ws.column_dimensions['I'].width = 2    # 2
        ws.column_dimensions['J'].width = 14
        ws.column_dimensions['K'].width = 10
        ws.column_dimensions['L'].width = 2    # 3
        ws.column_dimensions['M'].width = 14
        ws.column_dimensions['N'].width = 10
        ws.column_dimensions['O'].width = 2    # 4
        ws.column_dimensions['P'].width = 14
        ws.column_dimensions['Q'].width = 10
        ws.column_dimensions['R'].width = 2    # 5
        ws.column_dimensions['S'].width = 14
        ws.column_dimensions['T'].width = 10
        ws.column_dimensions['U'].width = 2    # 6
        ws.column_dimensions['V'].width = 14
        ws.column_dimensions['W'].width = 10


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

        # そのままコピーできない
        # # ２列目～
        # for column_number, column_name in enumerate(self._gt_table.df.columns.values, 2):
        #     ws[f'{xl.utils.get_column_letter(column_number)}{row_number}'] = column_name
        ws[f'{xl.utils.get_column_letter(1)}{row_number}'] = 'No'
        ws[f'{xl.utils.get_column_letter(2)}{row_number}'] = '結果'
        ws[f'{xl.utils.get_column_letter(3)}{row_number}'] = '実現確率'
        # 4 は空列

        ws[f'{xl.utils.get_column_letter(5)}{row_number}'] = '開始前'

        # 6 は分岐線
        # 7 はedge
        ws[f'{xl.utils.get_column_letter(8)}{row_number}'] = '1局後'   # node
        ws[f'{xl.utils.get_column_letter(11)}{row_number}'] = '2局後'
        ws[f'{xl.utils.get_column_letter(14)}{row_number}'] = '3局後'
        ws[f'{xl.utils.get_column_letter(17)}{row_number}'] = '4局後'
        ws[f'{xl.utils.get_column_letter(20)}{row_number}'] = '5局後'
        ws[f'{xl.utils.get_column_letter(23)}{row_number}'] = '6局後'

        # ２行目
        # ------
        # 空行にする
        row_number = 2


    def on_each_gt_record(self, next_row_number, next_gt_record):
        """先読みで最初の１回を空振りさせるので、２行目から本処理です"""

        # 事前送り出し
        self.forward_cursor(next_gt_record=next_gt_record)

        curr_row_number = next_row_number - 1

        if self._curr_gt_record.no is None:
            print(f"[{datetime.datetime.now()}] {curr_row_number=} 現在レコードのnoがナンだから無視")
            pass


        else:
            # 色の参考： 📖 [Excels 56 ColorIndex Colors](https://www.excelsupersite.com/what-are-the-56-colorindex-colors-in-excel/)
            node_bgcolor = PatternFill(patternType='solid', fgColor='FFFFCC')

            # 罫線
            #
            #   style に入るもの： 'dashDot', 'dashDotDot', 'double', 'hair', 'dotted', 'mediumDashDotDot', 'dashed', 'mediumDashed', 'slantDashDot', 'thick', 'thin', 'medium', 'mediumDashDot'
            #
            side = Side(style='thick', color='000000')
            red_side = Side(style='thick', color='FF0000')
            orange_side = Side(style='thick', color='FFCC00')
            green_side = Side(style='thick', color='00FF00')
            blue_side = Side(style='thick', color='0000FF')
            yellow_side = Side(style='thick', color='FFFF00')
            # 親への接続は赤
            border_to_parent = Border(bottom=red_side)
            # 子への水平接続はオレンジ
            under_border_to_child_horizontal = Border(bottom=orange_side)
            # 子へのダウン接続はブルー
            under_border_to_child_down = Border(bottom=blue_side)
            leftside_border_to_child_down = Border(left=blue_side)
            # 子への垂直接続はイエロー
            l_letter_border_to_child_vertical = Border(left=yellow_side, bottom=yellow_side)
            leftside_border_to_child_vertical = Border(left=yellow_side)
            # 子へのアップ接続はグリーン
            l_letter_border_to_child_up = Border(left=green_side, bottom=green_side)

            upside_node_border = Border(top=side, left=side, right=side)
            downside_node_border = Border(bottom=side, left=side, right=side)


            # 変数名短縮
            ws = self._gt_wb_wrapper.worksheet


            # ３行目～６行目
            # -------------
            # データは３行目から、１かたまり３行を使って描画する
            row1_th = curr_row_number * 3 + 3
            row2_th = curr_row_number * 3 + 3 + 1
            row3_th = curr_row_number * 3 + 3 + 2
            three_row_numbers = [row1_th, row2_th, row3_th]

            # 行の高さ設定
            # height の単位はポイント。昔のアメリカ人が椅子に座ってディスプレイを見たとき 1/72 インチに見える大きさが 1ポイント らしいが、そんなんワカラン。目視確認してほしい
            ws.row_dimensions[row1_th].height = 13
            ws.row_dimensions[row2_th].height = 13
            ws.row_dimensions[row3_th].height = 6

            ws[f'A{row1_th}'].value = self._curr_gt_record.no
            ws[f'B{row1_th}'].value = self._curr_gt_record.result


            # TODO C列には確率を入れたい。あとで入れる
            # TODO D列は空列にしたい
            # TODO E列の上の方の行には 1 を入れたい


            def draw_node(round_th, three_column_names, three_row_numbers):
                """
                Parameters
                ----------
                round_th : int
                    第何局後
                
                Return
                ------
                nd : GameTreeNode
                    対象ノード
                """

                prev_nd = self._prev_gt_record.node_at(round_th - 1)
                nd = self._curr_gt_record.node_at(round_th - 1)

                if nd is None:
                    print(f"[{datetime.datetime.now()}] {curr_row_number=}  nd がナンのノードは無視")
                    return nd

                elif pd.isnull(nd.face):
                    print(f"[{datetime.datetime.now()}] {curr_row_number=}  face が NaN のノードは無視")
                    return nd

                elif pd.isnull(nd.rate):
                    print(f"[{datetime.datetime.now()}] {curr_row_number=}  rate が NaN のノードは無視")
                    return nd

                elif prev_nd is None:
                    # 前行が無ければ描画
                    pass

                elif nd.rate == prev_nd.rate:
                    print(f"[{datetime.datetime.now()}] {curr_row_number=}  前行の同ラウンドと rate が同じなら無視")
                    return nd


                # 以下、描画
                print(f"[{datetime.datetime.now()}] {self._curr_gt_record.no}行目 {round_th}局後 ノード描画  {curr_row_number=}")

                def edge_text(node):
                    if node.face == 'h':
                        face = '表'
                    elif node.face == 't':
                        face = '裏'
                    elif node.face == 'f':
                        face = '失敗'
                    else:
                        raise ValueError(f"{node.face=}")
                    
                    if node.winner == 'A':
                        winner = '(Ａさん'
                    elif node.winner == 'B':
                        winner = '(Ｂさん'
                    elif node.winner == 'N':
                        winner = ''
                    else:
                        raise ValueError(f"{node.winner=}")

                    if node.pts != -1:
                        pts = f"{node.pts:.0f}点)" # FIXME 小数部を消してる。これで誤差で丸めを間違えるケースはあるか？
                    else:
                        pts = ''

                    return f"{face}{winner}{pts}"

                cn1 = three_column_names[0]
                cn2 = three_column_names[1]
                cn3 = three_column_names[2]
                row1_th = three_row_numbers[0]
                row2_th = three_row_numbers[1]
                row3_th = three_row_numbers[2]

                # １列目：親ノードから伸びてきた枝
                #
                #   .
                # --...
                #   .
                #
                # 前ラウンドにノードがあれば、接続線を引く
                #
                if GameTreeView.can_connect_to_parent(
                        curr_gt_record=self._curr_gt_record,
                        prev_gt_record=self._prev_gt_record,
                        round_th=round_th):
                    ws[f'{cn1}{row1_th}'].border = border_to_parent
                

                # ２列目：分岐したエッジ
                ws[f'{cn2}{row1_th}'].value = edge_text(node=nd)

                # 子ノードへの接続は４種類の線がある
                #
                # (1) Horizontal
                #   .    under_border
                # ...__  
                #   .    None
                #   .    None
                #
                # (2) Down
                #   .    under_border
                # ..+__  
                #   |    leftside_border
                #   |    leftside_border
                #
                # (3) Vertical
                #   |    l_letter_border
                # ..+__  
                #   |    leftside_border
                #   |    leftside_border
                #
                # (4) Up
                #   |    l_letter_border
                # ..+__  
                #   .    None
                #   .    None
                #
                kind = GameTreeView.get_kind_connect_to_child(
                        prev_gt_record=self._prev_gt_record,
                        curr_gt_record=self._curr_gt_record,
                        next_gt_record=self._next_gt_record,
                        round_th=round_th)

                if kind == 'Horizontal':
                    ws[f'{cn2}{row1_th}'].border = under_border_to_child_horizontal
                
                elif kind == 'Down':
                    ws[f'{cn2}{row1_th}'].border = under_border_to_child_down
                    ws[f'{cn2}{row2_th}'].border = leftside_border_to_child_down
                    ws[f'{cn2}{row3_th}'].border = leftside_border_to_child_down

                elif kind == 'Vertical':
                    ws[f'{cn2}{row1_th}'].border = l_letter_border_to_child_vertical
                    ws[f'{cn2}{row2_th}'].border = leftside_border_to_child_vertical
                    ws[f'{cn2}{row3_th}'].border = leftside_border_to_child_vertical

                elif kind == 'Up':
                    ws[f'{cn2}{row1_th}'].border = l_letter_border_to_child_up

                else:
                    raise ValueError(f"{nd.face=}")

                # ３列目：箱
                ws[f'{cn3}{row1_th}'].value = nd.rate
                ws[f'{cn3}{row1_th}'].fill = node_bgcolor
                ws[f'{cn3}{row1_th}'].border = upside_node_border
                ws[f'{cn3}{row2_th}'].fill = node_bgcolor
                ws[f'{cn3}{row2_th}'].border = downside_node_border

                return nd


            # 根ノード
            # -------
            if curr_row_number == 0:
                ws[f'E{row1_th}'].value = 1
                ws[f'E{row1_th}'].fill = node_bgcolor
                ws[f'E{row1_th}'].border = upside_node_border
                ws[f'E{row2_th}'].fill = node_bgcolor
                ws[f'E{row2_th}'].border = downside_node_border


            # それ以外のノード
            # ---------------

            # 実現確率
            rate = None


            # 1局後
            # -----
            nd = draw_node(
                    round_th=1,
                    three_column_names=['F', 'G', 'H'],
                    three_row_numbers=three_row_numbers)

            if not pd.isnull(nd.rate):
                rate = nd.rate


            # 2局後
            # -----
            nd = draw_node(
                    round_th=2,
                    three_column_names=['I', 'J', 'K'],
                    three_row_numbers=three_row_numbers)

            if not pd.isnull(nd.rate):
                rate = nd.rate


            # 3局後
            # -----
            nd = draw_node(
                    round_th=3,
                    three_column_names=['L', 'M', 'N'],
                    three_row_numbers=three_row_numbers)

            if not pd.isnull(nd.rate):
                rate = nd.rate


            # 4局後
            # -----
            nd = draw_node(
                    round_th=4,
                    three_column_names=['O', 'P', 'Q'],
                    three_row_numbers=three_row_numbers)

            if not pd.isnull(nd.rate):
                rate = nd.rate


            # 5局後
            # -----
            nd = draw_node(
                    round_th=5,
                    three_column_names=['R', 'S', 'T'],
                    three_row_numbers=three_row_numbers)

            if not pd.isnull(nd.rate):
                rate = nd.rate


            # 6局後
            # -----
            nd = draw_node(
                    round_th=6,
                    three_column_names=['U', 'V', 'W'],
                    three_row_numbers=three_row_numbers)

            if not pd.isnull(nd.rate):
                rate = nd.rate


            # 実現確率
            # --------
            ws[f'C{row1_th}'].value = rate


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


        # GTテーブル
        gt_table, gt_file_read_result = GameTreeTable.from_csv(
                spec=spec,
                span=specified_series_rule.step_table.span,
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD),
                new_if_it_no_exists=False)

        if gt_file_read_result.is_file_not_found:
            raise ValueError(f"GTファイルが見つかりません {gt_file_read_result.file_path=}")


        print(f"""\
gt_table:
{gt_table}""")


        automation = Automation(gt_table=gt_table, gt_wb_wrapper=gt_wb_wrapper)

        # GTWB の Sheet シートへのヘッダー書出し
        automation.on_header()

        # GTWB の Sheet シートへの各行書出し
        gt_table.for_each(on_each=automation.on_each_gt_record)

        # 最終行の実行
        automation.on_each_gt_record(next_row_number=len(gt_table.df), next_gt_record=GameTreeRecord.new_empty())

        # GTWB ファイルの保存
        gt_wb_wrapper.save()


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
