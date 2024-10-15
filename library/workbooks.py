import os
import openpyxl as xl


from library.file_paths import GameTreeWorkbookFilePaths


class GameTreeWorkbookWrapper():
    """［ゲームツリー］ワークブック（.xlsx）"""


    def __init__(self, wb_file_path):
        """初期化"""
        self._wb_file_path = wb_file_path
        self._wb = None
        self._current_ws = None


    @staticmethod
    def instantiate(spec, span, t_step, h_step):
        """インスタンス生成"""

        # ワークブック（.xlsx）ファイルへのパス
        wb_file_path = GameTreeWorkbookFilePaths.as_workbook(
                spec=spec,
                span=span,
                t_step=t_step,
                h_step=h_step)

        return GameTreeWorkbookWrapper(
                wb_file_path=wb_file_path)


    def load_workbook(self):
        """ワークブック（.xlsx）ファイル読込"""
        
        # ファイルが既存なら読込
        if os.path.isfile(self._wb_file_path):
            try:
                self._wb = xl.load_workbook(filename=self._wb_file_path)
            except KeyError as e:
                print(f"""\
{e}
{self._wb_file_path=}
""")
                raise

        # ファイルが存在しなければ新規作成
        else:
            # ワークブックの作成
            self._wb = xl.Workbook()
        
        return self._wb


    def create_sheet(self, sheet_name, shall_overwrite=False):
        """シート作成

        Parameters
        ----------
        sheet_name : str
            シートの名前
        """

        # もしシートが既存なら削除する
        if shall_overwrite:
            if sheet_name in self._wb.sheetnames:
                del self._wb[sheet_name]

        self._current_ws = self._wb.create_sheet(title=sheet_name)
        return self._current_ws


    def save(self):
        """ワークブック（.xlsx）ファイルの保存
        
        Returns
        -------
        wb_file_path : str
            ファイルパス
        """
        self._wb.save(self._wb_file_path)
        return self._wb_file_path
