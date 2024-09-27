#
# python generate_class.py
#
# class のコーディングの手間を省くためのものです。
# テンプレートにCSVを流し込みます。
#
import traceback
import pandas as pd


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
                df = pd.read_csv(DATA_CSV_FILE_PATH, encoding="utf8")


                # とりあえず、テキストをファイルへ保存するための簡単な書き方
                with open(LOG_FILE_PATH, 'a', encoding='utf8') as f:

                    # データを１行ずつ書き出していく
                    for     property_name in\
                        df['property_name']:


                        filled_text = template.replace('{{property_name}}', property_name)
                        print(filled_text)
                        f.write(f"{filled_text}\n")    # 末尾に改行を付けて保存


                print("おわり。")


        except Exception as err:
                print(f"""\
おお、残念！　例外が投げられてしまった！  
{err=}  {type(err)=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")