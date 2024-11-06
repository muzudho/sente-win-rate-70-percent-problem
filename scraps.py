#
# python scraps.py convert_tp
#
# スクラップス
#

import traceback
import datetime
import sys

from scripts.scraps.convert_tp import execute as convert_tp
from scripts.scraps.convert_tpr import execute as convert_tpr
from scripts.scraps.convert_vrd import execute as convert_vrd


########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        args = sys.argv

        if 1 < len(args):

            if args[1] == 'convert_tp':
                convert_tp()


            elif args[1] == 'convert_tpr':
                convert_tpr()


            elif args[1] == 'convert_vrd':
                convert_vrd()


            else:
                raise ValueError(f'unsupported {args[1]=}')
        
        else:
            execute_manual()


    except Exception as err:
        print(f"""\
[{datetime.datetime.now()}] おお、残念！　例外が投げられてしまった！
{type(err)=}  {err=}

以下はスタックトレース表示じゃ。
{traceback.format_exc()}
""")
