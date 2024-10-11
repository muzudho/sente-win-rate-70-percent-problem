#
# python generate_record_class.py
#
# class のコーディングの手間を省くためのものです。
# テンプレートにCSVを流し込みます。
#
# data/class_properties.csv ファイルにプロパティー名を羅列してください。先頭行は `property_name` という列名であることに注意してください
#
#
import traceback
import pandas as pd
from library import RenamingBackup


DATA_CSV_FILE_PATH = 'data/class_properties.csv'
TEMPLATE_TXT_FILE_PATH = 'resources/class_property_template.txt'
LOG_FILE_PATH = 'logs/class_properties.log'


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    try:
        # ファイル名の一部が入力されます
        file_path = input(f"""\
予め、データをCSV形式で {DATA_CSV_FILE_PATH} ファイルに書き込んで用意しています。

また、データを書き出す書式を書いた {TEMPLATE_TXT_FILE_PATH} ファイルを用意しています。
これはテンプレートと呼びます。

これから、テンプレートにデータを流し込んで、 {LOG_FILE_PATH} ファイルへ書き出します。

それでは、エンター・キーを打鍵してみてください。
? """)


        # テンプレート・ファイルを先に読込
        with open(TEMPLATE_TXT_FILE_PATH, 'r', encoding='utf8') as f:
            # NOTE テキストファイルの末尾に改行が入っていると、表示時に改行されます。改行されたくない場合は、ファイルの末尾に改行を入れないようにしてください
            template = f.read()


            # データ・ファイルを読み込んで、データ・フレームにして返す
            renaming_backup = RenamingBackup(file_path=DATA_CSV_FILE_PATH)
            renaming_backup.rollback_if_file_crushed()
            df = pd.read_csv(DATA_CSV_FILE_PATH, encoding="utf8",
                dtype={'property_name' : 'object'})


            property_name_list = []

            for     property_name in\
                df['property_name']:
                property_name_list.append(property_name)


            # とりあえず、テキストをファイルへ保存するための簡単な書き方
            with open(LOG_FILE_PATH, 'w', encoding='utf8') as f:


                f.write(f"""\
class Record():


    def __init__(self, {', '.join(property_name_list)}):
""")                

                for property_name in property_name_list:
                    f.write(f"""\
        self._{property_name} = {property_name}
""")

                # 空行
                f.write(f"""\


""")

                # データを１行ずつ書き出していく
                for property_name in property_name_list:
                    filled_text = template.replace('{{property_name}}', property_name)
                    print(filled_text)
                    f.write(f"{filled_text}\n")    # 末尾に改行を付けて保存


                line_1 = '  ,     '.join(property_name_list)
                line_2 = """df['""" + """'], df['""".join(property_name_list) + """']"""

                f.write(f'''\
class Table():


    @staticmethod
    def for_each(df, on_each):
        """
        Parameters
        ----------
        df : DataFrame
            データフレーム
        on_each : func
            record 引数を受け取る関数
        """
        for         {line_1} in\\
            zip({line_2}):

            # レコード作成
            record = Record(
''')

                for index_th, property_name in enumerate(property_name_list, 1):
                    # 末尾カンマ
                    if index_th < len(property_name_list):
                        f.write(f'''\
                    {property_name}={property_name},
''')

                    # 末尾閉じ括弧
                    else:
                        f.write(f'''\
                    {property_name}={property_name})
''')


                f.write(f'''\

            on_each(record)
''')

            print("おわり。")


    except Exception as err:
        print(f"""\
おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
