#
# 生成
# python generate_even_when_frozen_turn.py
#
#   引き分けは考慮していない。
#   手番を交代しない方式。
#   先後固定制での、［黒勝ちだけでの対局数］と、［白勝ちだけでの対局数］を探索する。
#

import traceback
import random
import math
import pandas as pd

from library import BLACK, WHITE, coin, n_bout_when_frozen_turn, n_round_when_frozen_turn, round_letro, PointsConfiguration
from views import print_when_generate_when_frozen_turn


LOG_FILE_PATH = 'output/generate_even_when_frozen_turn.log'
CSV_FILE_PATH = './data/generate_even_when_frozen_turn.csv'

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
    for p, best_new_p, best_new_p_error, best_round_count, best_b_step, best_w_step, best_span, best_w_time, best_number_of_longest_bout, process in zip(df['p'], df['new_p'], df['new_p_error'], df['round_count'], df['b_step'], df['w_step'], df['span'], df['w_time'], df['number_of_longest_bout'], df['process']):

        is_update = False

        # ［黒勝ちだけでの対局数］は計算で求めます
        best_b_time = best_number_of_longest_bout-(best_w_time-1)

        is_automatic = best_new_p_error >= limit_of_error or best_number_of_longest_bout == 0 or best_round_count < 2_000_000 or best_w_time == 0

        # アルゴリズムで求めるケース
        if is_automatic:

            is_cutoff = False

            # ［最長対局数］
            for number_of_longest_bout in range(best_number_of_longest_bout, 101):

                # １本勝負のときだけ、白はｎ本－１ではない
                if number_of_longest_bout == 1:
                    end_w_time = 2
                else:
                    end_w_time = number_of_longest_bout

                for w_time in range(1, end_w_time):

                    # FIXME ［黒勝ちだけでの対局数］は計算で求めます。計算合ってる？
                    b_time = number_of_longest_bout-(w_time-1)

                    # ［勝ち点ルール］の構成
                    points_configuration = PointsConfiguration.let_points_from_repeat(b_time, w_time)

                    black_win_count = n_round_when_frozen_turn(
                            p=p,
                            number_of_longest_bout=number_of_longest_bout,
                            b_time=b_time,
                            w_time=w_time,
                            round_count=best_round_count)
                    
                    #print(f"{black_win_count=}  {best_round_count=}  {black_win_count / best_round_count=}")
                    new_p = black_win_count / best_round_count
                    new_p_error = abs(new_p - 0.5)

                    if new_p_error < best_new_p_error:
                        is_update = True
                        best_new_p = new_p
                        best_new_p_error = new_p_error
                        best_points_configuration = points_configuration
                        best_b_time = b_time
                        best_w_time = w_time
                        best_number_of_longest_bout = number_of_longest_bout
                    
                        # 計算過程
                        one_process_text = f'[{best_new_p_error:6.4f} {best_points_configuration.b_step}黒 {best_points_configuration.w_step}白 {best_points_configuration.span}目]'
                        print(one_process_text, end='', flush=True) # すぐ表示

                        # ［計算過程］列を更新
                        #
                        #   途中の計算式。半角空白区切り
                        #
                        if isinstance(process, str):
                            all_processes_text = f"{process} {one_process_text}"
                        else:
                            all_processes_text = one_process_text
                        # ［計算過程］列を更新
                        df.loc[df['p']==p, ['process']] = all_processes_text

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

        elif not is_update:
            print(f"先手勝率：{p*100:2} ％  （更新なし）")

        else:
            print_when_generate_when_frozen_turn(p, best_new_p, best_new_p_error, best_round_count, best_points_configuration)

            # データチェック
            if best_points_configuration.let_number_of_longest_bout_when_frozen_turn() != best_number_of_longest_bout:
                raise ValueError(f"実践値と理論値が異なる {best_points_configuration.let_number_of_longest_bout_when_frozen_turn()=}  {best_number_of_longest_bout=}")

            # データフレーム更新
            # -----------------

            # ［調整後の表が出る確率］列を更新
            df.loc[df['p']==p, ['new_p']] = best_new_p

            # ［調整後の表が出る確率の５割との誤差］列を更新
            df.loc[df['p']==p, ['new_p_error']] = best_new_p_error

            # ［黒勝ちの価値］列を更新
            df.loc[df['p']==p, ['b_step']] = points_configuration.b_step

            # ［白勝ちの価値］列を更新
            df.loc[df['p']==p, ['w_step']] = points_configuration.w_step

            # ［目標の点（先後固定制）］列を更新 
            df.loc[df['p']==p, ['span']] = points_configuration.span

            # ［黒勝ちだけでの対局数］列を更新
            df.loc[df['p']==p, ['b_time']] = best_b_time

            # ［白勝ちだけでの対局数］列を更新
            df.loc[df['p']==p, ['w_time']] = best_w_time

            # ［最長対局数］列を更新
            #
            #   FIXME 削除方針。これを使うよりも、 b_step, w_step, span を使った方がシンプルになりそう
            #
            df.loc[df['p']==p, ['number_of_longest_bout']] = best_number_of_longest_bout

            # CSV保存
            df.to_csv(CSV_FILE_PATH,
                    # ［計算過程］列は長くなるので末尾に置きたい
                    columns=['p', 'new_p', 'new_p_error', 'round_count', 'b_step', 'w_step', 'span', 'b_time', 'w_time', 'number_of_longest_bout', 'process'],
                    index=False)    # NOTE 高速化のためか、なんか列が追加されるので、列が追加されないように index=False を付けた


########################################
# コマンドから実行時
########################################


if __name__ == '__main__':
    """コマンドから実行時"""

    try:

        df = pd.read_csv(CSV_FILE_PATH, encoding="utf8")
        #
        # NOTE pandas のデータフレームの列の型の初期値が float なので、それぞれ設定しておく
        #
        df['p'].astype('float')
        df['new_p'].fillna(0.0).astype('float')
        df['new_p_error'].fillna(0.0).astype('float')
        df['round_count'].fillna(0).astype('int')
        df['b_step'].fillna(0).astype('int')
        df['w_step'].fillna(0).astype('int')
        df['span'].fillna(0).astype('int')
        df['b_time'].fillna(0).astype('int')
        df['w_time'].fillna(0).astype('int')
        df['number_of_longest_bout'].fillna(0).astype('int')
        df['process'].fillna('').astype('string')
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
            worst_new_p_error = df['new_p_error'].max()
            print(f"{worst_new_p_error=}")

            # とりあえず、［調整後の表が出る確率］が［最大エラー］値の半分未満になるよう目指す
            #
            #   NOTE P=0.99 の探索は、 p=0.50～0.98 を全部合わせた処理時間よりも、時間がかかるかも。だから p=0.99 のケースだけに合わせて時間調整するといいかも。
            #   NOTE エラー値を下げるときに、８本勝負の次に９本勝負を見つけられればいいですが、そういうのがなく次が１５本勝負だったりするような、跳ねるケースでは処理が長くなりがちです。リミットをゆっくり下げればいいですが、どれだけ気を使っても避けようがありません
            #
            # 半分、半分でも速そうなので、１０分の９を繰り返す感じで。
            limit_of_error = worst_new_p_error * 9 / 10

            iteration_deeping(df, limit_of_error)


    except Exception as err:
        print(f"[unexpected error] {err=}  {type(err)=}")

        # スタックトレース表示
        print(traceback.format_exc())

        raise
