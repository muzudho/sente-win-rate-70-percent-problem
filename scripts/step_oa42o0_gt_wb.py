import math
import datetime
import pandas as pd
from openpyxl.styles import PatternFill, Font
from openpyxl.styles.borders import Border, Side
from openpyxl.styles.alignment import Alignment
import xltree as tr

from library import HEAD, TAIL
from library.file_paths import GameTreeWorkbookFilePaths, GameTreeFilePaths


class Automation():


    def execute(self, spec, specified_series_rule, debug_write=False):


        # ワークブック（.xlsx）ファイルへのパス
        wb_file_path = GameTreeWorkbookFilePaths.as_workbook(
                spec=spec,
                span=specified_series_rule.step_table.span,
                t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD))

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
        with tr.prepare_workbook(target=wb_file_path, mode='w', settings=settings) as b:

            csv_file_path=GameTreeFilePaths.as_csv(
                    spec=spec,
                    span=specified_series_rule.step_table.span,
                    t_step=specified_series_rule.step_table.get_step_by(face_of_coin=TAIL),
                    h_step=specified_series_rule.step_table.get_step_by(face_of_coin=HEAD))

            # テーブル読取
            df = pd.read_csv(csv_file_path, encoding="utf8", index_col=['no'])
            if debug_write:
                print(df)

            # 読取元CSVを指定し、ワークシートハンドル取得
            with b.prepare_worksheet(target='Tree', based_on=csv_file_path) as s:

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


            # 読取元CSVを指定し、ワークシートハンドル取得
            with b.prepare_worksheet(target='Summary', based_on=csv_file_path) as s:
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


                # 最長の文字数も図っておく
                if len(df) == 0:
                    max_length_of_a = 0
                    max_length_of_b = 0
                else:
                    max_length_of_a = df['result'].str.len().max()  # 文字列の長さ
                    max_length_of_b = df['sum_rate'].abs().astype(str).str.len().max()-1    # 浮動小数点数の長さ


                # Total を集計
                total_sum_rate = df['sum_rate'].sum()


                # ワークシートへの出力
                # ------------------

                # 列名
                ws['A1'] = 'result'
                ws['B1'] = 'sum_rate'

                # 列幅の自動調整
                ws.column_dimensions['A'].width = max_length_of_a * 2       # 日本語
                ws.column_dimensions['B'].width = max_length_of_b * 1.2     # 浮動小数点数

                # ヘッダーの背景色
                fill = PatternFill(patternType='solid', fgColor='111111')
                ws['A1'].fill = fill
                ws['B1'].fill = fill

                # ヘッダーの文字色
                font = Font(color='EEEEEE')
                ws['A1'].font = font
                ws['B1'].font = font

                # データ部のコピー
                for row_no in range(0, len(df)):
                    result = df.at[row_no, 'result']
                    sum_rate = df.at[row_no, 'sum_rate']
                    # データ部は 2nd 行目から
                    ws[f'A{row_no + 2}'] = result
                    ws[f'B{row_no + 2}'] = sum_rate
                    ws[f'B{row_no + 2}'].alignment = Alignment(horizontal='left')

                # データ部のトータル行の追加
                row_no += 1
                ws[f'A{row_no + 2}'] = 'Total'
                ws[f'B{row_no + 2}'] = total_sum_rate
                ws[f'B{row_no + 2}'].alignment = Alignment(horizontal='left')

                # データ部のトータル行を区切る罫線
                side = Side(style='thick', color='111111')
                border = Border(top=side)
                ws[f'A{row_no + 2}'].border = border
                ws[f'B{row_no + 2}'].border = border


            # 何かワークシートを１つ作成したあとで、最初から入っている 'Sheet' を削除
            b.remove_worksheet(target='Sheet')

            # 保存
            b.save_workbook()

            print(f"[{datetime.datetime.now()}] Please look {wb_file_path}")
