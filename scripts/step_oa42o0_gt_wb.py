import math
import datetime
import pandas as pd
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.borders import Border, Side
from openpyxl.styles.alignment import Alignment
import xltree as tr

from library import HEAD, TAIL
from library.file_paths import GameTreeWorkbookFilePaths, GameTreeFilePaths, GameTreeCheckedFilePaths


class GeneratorOfGTWB():


    @staticmethod
    def instantiate(series_rule):
        # 出力するワークブック（.xlsx）ファイルへのパス
        wb_file_path = GameTreeWorkbookFilePaths.as_workbook(
                spec=series_rule.spec,
                span=series_rule.step_table.span,
                t_step=series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=series_rule.step_table.get_step_by(face_of_coin=HEAD))

        # 元となる CSVファイルパス
        source_csv_file_path=GameTreeFilePaths.as_csv(
                spec=series_rule.spec,
                span=series_rule.step_table.span,
                t_step=series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=series_rule.step_table.get_step_by(face_of_coin=HEAD))

        # チェック済みの CSVファイルパス
        checked_csv_file_path=GameTreeCheckedFilePaths.as_csv(
                spec=series_rule.spec,
                span=series_rule.step_table.span,
                t_step=series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=series_rule.step_table.get_step_by(face_of_coin=HEAD))

        return GeneratorOfGTWB(series_rule=series_rule, wb_file_path=wb_file_path, source_csv_file_path=source_csv_file_path, checked_csv_file_path=checked_csv_file_path)


    def __init__(self, series_rule, wb_file_path, source_csv_file_path, checked_csv_file_path):
        self._series_rule = series_rule
        self._wb_file_path = wb_file_path
        self._source_csv_file_path = source_csv_file_path
        self._checked_csv_file_path = checked_csv_file_path


    @property
    def workbook_file_path(self):
        return self._wb_file_path


    @property
    def source_csv_file_path(self):
        return self._source_csv_file_path


    @property
    def checked_csv_file_path(self):
        return self._checked_csv_file_path


    def write_workbook(self, debug_write=False):
        """ワークブック（.xlsx）ファイルを書き出す

        TODO 高速化したい
        """


        # 構成
        settings ={
            # # 列の幅
            # 'no_width':                         4,      # A列の幅。no列
            # 'row_header_separator_width':       3,      # B列の幅。空列
            # 'node_width':                       20,     # 例：C, F, I ...列の幅。ノードの箱の幅
            # 'parent_side_edge_width':           2,      # 例：D, G, J ...列の幅。エッジの水平線のうち、親ノードの方
            # 'child_side_edge_width':            4,      # 例：E, H, K ...列の幅。エッジの水平線のうち、子ノードの方

            # # 行の高さ
            # 'header_height':                    13,     # 第１行。ヘッダー
            # 'column_header_separator_height':   13,     # 第２行。空行
        }

        # 出力先ワークブックを指定し、ワークブックハンドル取得
        with tr.prepare_workbook(target=self._wb_file_path, mode='w', settings=settings) as b:

            # テーブル読取
            df = pd.read_csv(self._source_csv_file_path, encoding="utf8", index_col=['no'])
            if debug_write:
                print(df)


            ############
            # MARK: Tree
            ############

            # 読取元CSVを指定し、ワークシートハンドル取得
            with b.prepare_worksheet(target='Tree', based_on=self._source_csv_file_path) as s:

                # ワークシートへ木構造図を描画
                s.render_tree()

                # 集計を行いたい。ツリー構造の全ての葉を取得する                
                all_leaf_entries = []

                def search(all_leaf_entries, entry):
                    """再帰的に子ノードを表示"""

                    if debug_write:
                        print(f"{entry.edge_text=}  {entry.node_text=}  の子要素数={len(entry.child_entries)}  TOTAL {len(all_leaf_entries)=}")

                    for child_entry in entry.child_entries.values():
                        # 葉ノード
                        if not child_entry.has_children():
                            if debug_write:
                                print("葉ノード")
                            all_leaf_entries.append(child_entry)
                        
                        # 中間ノード
                        else:
                            if debug_write:
                                print("中間ノード")
                            search(all_leaf_entries=all_leaf_entries, entry=child_entry) # 再帰

                if debug_write:
                    # 木構造の簡易ターミナル表示
                    print(s.forest._stringify_like_tree(''))
                        

                # 各根について
                for root_entry in s.forest.multiple_root_entry.values():
                    search(all_leaf_entries=all_leaf_entries, entry=root_entry)


                if debug_write:
                    print(f"葉の探索結果  {len(all_leaf_entries)=}")


                # leaf_th と result列 を紐づける
                rate_list_by_result = {}
                for leaf in all_leaf_entries:
                    result = df.at[leaf.leaf_th, 'result']
                    if debug_write:
                        print(f"葉テスト {leaf.node_text=}  {leaf.leaf_th=}  {result}")

                    if result not in rate_list_by_result:
                        rate_list_by_result[result] = []
                    
                    rate_list_by_result[result].append(float(leaf.node_text))

                # result 別に確率を高精度 sum する
                sum_rate_by_result = {}
                for result, rate_list in rate_list_by_result.items():
                    sum_rate = math.fsum(rate_list)
                    if debug_write:
                        print(f"{result=}  {sum_rate=}")
                    sum_rate_by_result[result] = sum_rate

                # 結果表示 ＆ Total検算
                total = math.fsum(sum_rate_by_result.values())
                if debug_write:
                    print(f"検算 {total=}")

                # エラーは常時表示するが、続行する
                if total != 1:
                    print(f"[error] total must be 1. but {total}")
                    #raise ValueError(f"total must be 1. but {total}")


            ###############
            # MARK: Summary
            ###############

            # 読取元CSVを指定し、ワークシートハンドル取得
            with b.prepare_worksheet(target='Summary', based_on=self._source_csv_file_path) as s:
                ws = s._ws  # 非公式な方法。将来的にサポートされるか分からない方法

                # データフレームの操作
                # ------------------

                # 操作が便利なので、pandas に移し替える
                records = []
                for result, sum_rate in sum_rate_by_result.items():
                    records.append([result, sum_rate])

                df = pd.DataFrame(records, columns=['result', 'sum_rate'])

                # sum_rate 列の値の大きい順に並び変える
                df.sort_values(['sum_rate', 'result'], inplace=True, ascending=[False, True])

                # 連番列を追加
                df['no'] = range(0, len(df))

                # 連番列を、（列を止めて）インデックスに変更
                df.set_index('no', inplace=True)

                # 列の並び替え
                #df = df[['result', 'sum_rate']]

                # デバッグ表示
                #print(df)


                # ワークシートへの出力
                # ------------------

                # 1th ヘッダー行
                self.write_header_of_top(df=df, ws=ws, destination_row_th=1)

                # 2nd Ａさん（シリーズを先手で始めた方）が優勝した率
                a_victory_rate_by_trio = self.get_a_victory_rate_by_trio(sum_rate_by_result=sum_rate_by_result)
                self.write_a_victory_rate_by_trio(a_victory_rate_by_trio=a_victory_rate_by_trio, ws=ws, destination_row_th=2)

                # 3nd Ｂさん（シリーズを後手で始めた方）が優勝した率
                b_victory_rate_by_trio = self.get_b_victory_rate_by_trio(sum_rate_by_result=sum_rate_by_result)
                self.write_b_victory_rate_by_trio(b_victory_rate_by_trio=b_victory_rate_by_trio, ws=ws, destination_row_th=3)

                # 4th 優勝が決まらなかった率
                no_victory_rate = self.get_no_victory_rate(sum_rate_by_result=sum_rate_by_result)
                self.write_no_victory_rate(no_victory_rate=no_victory_rate, ws=ws, destination_row_th=4)

                # 5th トータル行
                self.write_victory_total_by_trio(a_victory_rate_by_trio=a_victory_rate_by_trio, b_victory_rate_by_trio=b_victory_rate_by_trio, no_victory_rate=no_victory_rate, ws=ws, destination_row_th=5)

                # 6th 空行

                # 7th ヘッダー行
                self.write_header_of_section_and_adjust_column_width(df=df, ws=ws, destination_row_th=7)

                # 8th～: データ部のコピー
                for source_row_no in range(0, len(df)):
                    destination_row_th = source_row_no + 8

                    self.write_sections(
                            df=df,
                            ws=ws,
                            source_row_no=source_row_no,
                            destination_row_th=destination_row_th)


                # 詳細トータル行
                self.write_detail_total(
                        df=df,
                        ws = ws,
                        destination_row_th=destination_row_th + 1)


            # 何かワークシートを１つ作成したあとで、最初から入っている 'Sheet' を削除
            b.remove_worksheet(target='Sheet')

            # 保存
            b.save_workbook()

            print(f"[{datetime.datetime.now()}] Please look {self._wb_file_path}")


    def write_header_of_top(self, df, ws, destination_row_th):
        """トップのヘッダーを出力"""

        # 列名
        ws[f'A{destination_row_th}'] = 'name'
        ws[f'B{destination_row_th}'] = 'value'

        # ヘッダーの背景色
        fill = PatternFill(patternType='solid', fgColor='111111')
        ws[f'A{destination_row_th}'].fill = fill
        ws[f'B{destination_row_th}'].fill = fill

        # ヘッダーの文字色
        font = Font(color='EEEEEE')
        ws[f'A{destination_row_th}'].font = font
        ws[f'B{destination_row_th}'].font = font


    def write_header_of_section_and_adjust_column_width(self, df, ws, destination_row_th):
        """セクションのヘッダーを出力。列幅の自動調整"""

        # 列幅の自動調整
        # -------------

        # 最長の文字数を図ります
        if len(df) == 0:
            # max_length_of_a = 0
            max_length_of_b = 0
        else:
            # max_length_of_a = df['result'].str.len().max()  # 文字列の長さ
            max_length_of_b = df['sum_rate'].abs().astype(str).str.len().max()-1    # 浮動小数点数の長さ

        # 列名
        a_column_name = 'result'
        b_column_name = 'sum_rate'

        # 列名よりは長く
        # max_length_of_a = max(max_length_of_a, len(a_column_name))
        max_length_of_b = max(max_length_of_b, len(b_column_name))

        ws.column_dimensions['A'].width = 43    # 'Ａさん（シリーズを先手で始めた方）が優勝した率' が 43 ぐらい。    #max_length_of_a * 2       # 日本語
        ws.column_dimensions['B'].width = max_length_of_b * 1.2     # 浮動小数点数

        # 列名
        ws[f'A{destination_row_th}'] = a_column_name
        ws[f'B{destination_row_th}'] = b_column_name

        # ヘッダーの背景色
        fill = PatternFill(patternType='solid', fgColor='111111')
        ws[f'A{destination_row_th}'].fill = fill
        ws[f'B{destination_row_th}'].fill = fill

        # ヘッダーの文字色
        font = Font(color='EEEEEE')
        ws[f'A{destination_row_th}'].font = font
        ws[f'B{destination_row_th}'].font = font


    def get_a_victory_rate_by_trio(self, sum_rate_by_result):
        """Ａさん（シリーズを先手で始めた方）が優勝した率を算出"""
        # result 別に確率を高精度 sum する
        rate_list = []

        if '達成でＡさんの勝ち' in sum_rate_by_result:
            rate_list.append(sum_rate_by_result['達成でＡさんの勝ち'])
        
        if '勝ち点差でＡさんの勝ち' in sum_rate_by_result:
            rate_list.append(sum_rate_by_result['勝ち点差でＡさんの勝ち'])

        return math.fsum(rate_list)


    def write_a_victory_rate_by_trio(self, a_victory_rate_by_trio, ws, destination_row_th):
        """Ａさん（シリーズを先手で始めた方）が優勝した率を出力"""

        ws[f'A{destination_row_th}'] = 'Ａさん（シリーズを先手で始めた方）が優勝した率'
        ws[f'B{destination_row_th}'] = a_victory_rate_by_trio
        ws[f'B{destination_row_th}'].alignment = Alignment(horizontal='left')


    def get_b_victory_rate_by_trio(self, sum_rate_by_result):
        """Ｂさん（シリーズを後手で始めた方）が優勝した率を算出"""

        # result 別に確率を高精度 sum する
        rate_list = []

        if '達成でＢさんの勝ち' in sum_rate_by_result:
            rate_list.append(sum_rate_by_result['達成でＢさんの勝ち'])
        
        if '勝ち点差でＢさんの勝ち' in sum_rate_by_result:
            rate_list.append(sum_rate_by_result['勝ち点差でＢさんの勝ち'])

        return math.fsum(rate_list)


    def write_b_victory_rate_by_trio(self, b_victory_rate_by_trio, ws, destination_row_th):
        """Ｂさん（シリーズを後手で始めた方）が優勝した率を出力"""

        ws[f'A{destination_row_th}'] = 'Ｂさん（シリーズを後手で始めた方）が優勝した率'
        ws[f'B{destination_row_th}'] = b_victory_rate_by_trio
        ws[f'B{destination_row_th}'].alignment = Alignment(horizontal='left')


    def get_no_victory_rate(self, sum_rate_by_result):
        """優勝が決まらなかった率を算出"""

        if '勝者なし' in sum_rate_by_result:
            return sum_rate_by_result['勝者なし']
        
        return 0


    def write_no_victory_rate(self, no_victory_rate, ws, destination_row_th):
        """優勝が決まらなかった率を出力"""

        ws[f'A{destination_row_th}'] = '優勝が決まらなかった率'
        ws[f'B{destination_row_th}'] = no_victory_rate
        ws[f'B{destination_row_th}'].alignment = Alignment(horizontal='left')


    def write_victory_total_by_trio(self, a_victory_rate_by_trio, b_victory_rate_by_trio, no_victory_rate, ws, destination_row_th):
        """大分類トータル行を出力"""
        
        # Total を集計
        total_sum_rate = math.fsum([a_victory_rate_by_trio, b_victory_rate_by_trio, no_victory_rate])

        # データ部のトータル行の追加
        ws[f'A{destination_row_th}'] = 'Total'
        ws[f'B{destination_row_th}'] = total_sum_rate
        ws[f'B{destination_row_th}'].alignment = Alignment(horizontal='left')

        # データ部のトータル行を区切る罫線
        side = Side(style='thick', color='111111')
        border = Border(top=side)
        ws[f'A{destination_row_th}'].border = border
        ws[f'B{destination_row_th}'].border = border


    def write_sections(self, df, ws, source_row_no, destination_row_th):
        result = df.at[source_row_no, 'result']
        sum_rate = df.at[source_row_no, 'sum_rate']

        ws[f'A{destination_row_th}'] = result
        ws[f'B{destination_row_th}'] = sum_rate
        ws[f'B{destination_row_th}'].alignment = Alignment(horizontal='left')


    def write_detail_total(self, df, ws, destination_row_th):
        """詳細トータル行を出力"""

        # Total を集計
        total_sum_rate = df['sum_rate'].sum()

        # データ部のトータル行の追加
        ws[f'A{destination_row_th}'] = 'Total'
        ws[f'B{destination_row_th}'] = total_sum_rate
        ws[f'B{destination_row_th}'].alignment = Alignment(horizontal='left')

        # データ部のトータル行を区切る罫線
        side = Side(style='thick', color='111111')
        border = Border(top=side)
        ws[f'A{destination_row_th}'].border = border
        ws[f'B{destination_row_th}'].border = border
