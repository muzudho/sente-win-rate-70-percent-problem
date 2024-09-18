#
# 生成
# python generate_even_in_frozen_turn.py
#
#   引き分けは考慮していない。
#   手番を交代しない方式。
#   先手が勝つのに必要な先取本数と、後手が勝つのに必要な先取本数を探索する。
#

import traceback
import random
import math
import pandas as pd

from library import BLACK, WHITE, coin, n_bout_in_frozen_turn, n_round_in_frozen_turn, round_letro, PointRuleDescription


LOG_FILE_PATH = 'output/generate_even_in_frozen_turn.log'
CSV_FILE_PATH = './data/generate_even_in_frozen_turn.csv'

# 勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
OUT_OF_ERROR = 0.51


def iteration_deeping(df, limit_of_error):
    """反復深化探索の１セット

    Parameters
    ----------
    df : DataFrame
        データフレーム
    limit_of_error : float
        リミット
    """
    for p, best_new_p, best_new_p_error, best_max_bout_count, best_round_count, best_w_require, process in zip(df['p'], df['new_p'], df['new_p_error'], df['max_number_of_bout_in_frozen_turn'], df['round_count'], df['w_require'], df['process']):
        #print(f"{p=}  {best_new_p_error=}  {best_max_bout_count=}  {best_round_count=}  {best_w_require=}  {process=}  {type(process)=}")

        # 黒の必要先取数は計算で求めます
        best_b_require = best_max_bout_count-(best_w_require-1)

        is_automatic = best_new_p_error >= limit_of_error or best_max_bout_count == 0 or best_round_count < 2_000_000 or best_w_require == 0

        # アルゴリズムで求めるケース
        if is_automatic:

            is_cutoff = False

            # ［最長対局数（先後固定制）］
            for max_number_of_bout_in_frozen_turn in range(best_max_bout_count, 101):

                # １本勝負のときだけ、白はｎ本－１ではない
                if max_number_of_bout_in_frozen_turn == 1:
                    end_w_require = 2
                else:
                    end_w_require = max_number_of_bout_in_frozen_turn

                for w_require in range(1, end_w_require):

                    # FIXME 黒の必要先取数は計算で求めます
                    b_require = max_number_of_bout_in_frozen_turn-(w_require-1)

                    black_win_count = n_round_in_frozen_turn(
                        black_win_rate=p,
                        max_number_of_bout_in_frozen_turn=max_number_of_bout_in_frozen_turn,
                        b_require=b_require,
                        w_require=w_require,
                        round_count=best_round_count)
                    
                    #print(f"{black_win_count=}  {best_round_count=}  {black_win_count / best_round_count=}")
                    new_p = black_win_count / best_round_count
                    new_p_error = abs(new_p - 0.5)

                    if new_p_error < best_new_p_error:
                        best_new_p = new_p
                        best_new_p_error = new_p_error
                        best_max_bout_count = max_number_of_bout_in_frozen_turn
                        best_b_require = b_require
                        best_w_require = w_require
                    
                        # 進捗バー（更新時）
                        text = f'[{best_new_p_error:6.4f} 最長対局数{best_max_bout_count:2} {best_max_bout_count-best_w_require+1:2}黒 {best_w_require:2}白]'
                        print(text, end='', flush=True) # すぐ表示

                        # process 列を更新
                        #
                        #   途中の計算式。半角空白区切り
                        #
                        if isinstance(process, str):
                            df.loc[df['p']==p, ['process']] = f"{process} {text}"
                        else:
                            df.loc[df['p']==p, ['process']] = text

                        # 十分な答えが出たので探索を打ち切ります
                        if best_new_p_error < limit_of_error:
                            is_cutoff = True

                            # 進捗バー
                            print('x', end='', flush=True)

                            break

                if is_cutoff:
                    break

                # 進捗バー（ｎ本目）
                print('.', end='', flush=True)

            print() # 改行

        # 結果が設定されていれば、そのまま表示
        else:
            pass



        # 自動計算未完了
        if is_automatic and best_new_p_error == OUT_OF_ERROR:
            print(f"先手勝率：{p*100:2} ％  （自動計算未完了）")

        else:
            # 先手の勝ち点、後手の勝ち点、目標の勝ち点を求める
            point_rule_description = PointRuleDescription.let_points_from_require(best_b_require, best_w_require)

            print(f"先手勝率：{p*100:2.0f} ％ --調整後--> {best_new_p * 100:>7.04f} ％（± {best_new_p_error * 100:>7.04f}）  最長対局数{best_max_bout_count:2} {best_round_count:6}回  先手勝ち{point_rule_description.b_step:2.0f}点、後手勝ち{point_rule_description.w_step:2.0f}点の{point_rule_description.target_point:3.0f}点先取制", end='')
            if is_automatic:
                print(f"  （自動計算満了）")
            else:
                print(f"  （対象外。誤差十分）")

            # データフレーム更新
            # -----------------

            # ［調整後の表が出る確率］列を更新
            df.loc[df['p']==p, ['new_p']] = best_new_p

            # ［調整後の表が出る確率の５割との誤差］列を更新
            df.loc[df['p']==p, ['new_p_error']] = best_new_p_error

            # ［最長対局数（先後固定制）］列を更新
            df.loc[df['p']==p, ['max_number_of_bout_in_frozen_turn']] = best_max_bout_count

            #best_b_require は max_number_of_bout_in_frozen_turn と w_require から求まる

            # ［白が勝つのに必要な先取本数］列を更新
            df.loc[df['p']==p, ['w_require']] = best_w_require

        
        # CSV保存
        df.to_csv(CSV_FILE_PATH,
                index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        df = pd.read_csv(CSV_FILE_PATH, encoding="utf8")
        print(df)


        # 反復深化探索
        # ===========
        #
        #   ［エラー］が 0 になることを目指していますが、最初から 0 を目指すと、もしかするとエラーは 0 にならなくて、
        #   処理が永遠に終わらないかもしれません。
        #   そこで、［エラー］列は、一気に 0 を目指すのではなく、手前の目標を設定し、その目標を徐々に小さくしていきます。
        #   リミットを指定して、リミットより［エラー］が下回ったら、処理を打ち切ることにします
        #
        limit_of_error = OUT_OF_ERROR

        while 0.00009 < limit_of_error:
            # ［エラー］列で一番大きい値を取得します
            #
            #   ［調整後の表が出る確率］を 0.5 になるように目指します。［エラー］列は、［調整後の表が出る確率］と 0.5 の差の絶対値です
            #
            worst_nwe_p_error = df['new_p_error'].max()
            print(f"{worst_nwe_p_error=}")

            # とりあえず、［調整後の表が出る確率］が［最大エラー］値の半分未満になるよう目指す
            #
            #   NOTE P=0.99 の探索は、 p=0.50～0.98 を全部合わせた処理時間よりも、時間がかかるかも。だから p=0.99 のケースだけに合わせて時間調整するといいかも。
            #   NOTE エラー値を下げるときに、８本勝負の次に９本勝負を見つけられればいいですが、そういうのがなく次が１５本勝負だったりするような、跳ねるケースでは処理が長くなりがちです。リミットをゆっくり下げればいいですが、どれだけ気を使っても避けようがありません
            #
            # 半分、半分でも速そうなので、１０分の９を繰り返す感じで。
            limit_of_error = worst_nwe_p_error * 9 / 10

            iteration_deeping(df, limit_of_error)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
