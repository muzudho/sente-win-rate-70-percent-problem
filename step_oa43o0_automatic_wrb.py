# python step_oa43o0_automatic_wrb.py

########################################
# コマンドから実行時
########################################
if __name__ == '__main__':
    """コマンドから実行時"""

    try:
        pass

        # TODO game_tree_wb フォルダーを見る

        # TODO GTWB ワークブック（.xlsx）ファイルの Summary シートの B2 セル（先手勝率）を見る

        # TODO turn system, failure rate, p 毎に、 span, t_step, h_step 毎の先手勝率を sub_WRB ファイルに記録する

        # TODO （step44o0）sub_WRB ファイル毎の最小の先手勝率を集計し、 turn system, failure rate, p 毎に WRB ファイルに記録する

    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())
