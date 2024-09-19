#
# 生成 手番を交互にするパターン
# FIXME まだできてない
# python generate_even_when_alternating_turn.py
#
#   引き分けは考慮していない。
#
#   * Ａさんが勝つために必要な［黒勝ちだけでの対局数］
#   * Ａさんが勝つために必要な［白勝ちだけでの対局数］
#   * Ａさんが勝つために必要な［黒白の回数の合算］
#   * Ｂさんが勝つために必要な［黒勝ちだけでの対局数］
#   * Ｂさんが勝つために必要な［白勝ちだけでの対局数］
#   * Ｂさんが勝つために必要な［黒白の回数の合算］
#

import traceback
import random
import math
import pandas as pd

from library import BLACK, WHITE, coin, n_bout_when_frozen_turn, n_round_when_frozen_turn, round_letro, PointsConfiguration
from views import print_when_generate_even_when_alternating_turn


LOG_FILE_PATH = 'output/generate_even_when_alternating_turn.log'
CSV_FILE_PATH = './data/generate_even_when_alternating_turn.csv'

# 勝率は最低で 0.0、最大で 1.0 なので、0.5 との誤差は 0.5 が最大
OUT_OF_ERROR = 0.51

#
#   NOTE 手番を交代する場合、［最大ｎ本勝負］は、（Ａさんの［黒だけでの反復実施数］－１）＋（Ａさんの［白だけでの反復実施数］－１）＋（Ｂさんの［黒だけでの反復実施数］－１）＋（Ｂさんの［白だけでの反復実施数］－１）＋１ になる
#


def iteration_deeping(df, limit_of_error):
    """反復深化探索の１セット

    Parameters
    ----------
    df : DataFrame
        データフレーム
    limit_of_error : float
        リミット
    """
    for p, best_new_p, best_new_p_error, best_round_count, best_b_step, best_w_step, best_span, best_w_time, best_number_of_longest_bout_when_frozen_turn, process in zip(df['p'], df['new_p'], df['new_p_error'], df['round_count'], df['b_step'], df['w_step'], df['span'], df['w_time'], df['number_of_longest_bout_when_frozen_turn'], df['process']):

        #   交互に手番を替えるか、変えないかに関わらず、先手と後手の重要さは p で決まっている。
        #
        #   ［黒勝ちだけでの対局数］も、
        #   ［白勝ちだけでの対局数］数も、 p で決まっている。
        #
        #   ひとまず、リーチしている状況を考えてみよう。
        #
        #   'Ｘ' を、Ａさん（またはＢさん）の［黒勝ちだけでの対局数］、
        #   'ｘ' を、Ａさん（またはＢさん）の［白勝ちだけでの対局数］とする。
        #
        #   リーチしている状況は下の式のようになる。
        #
        #       ２（Ｘ－１）＋２（ｘー１）
        #
        #   ここに、点数の最小単位である　ｘ　を足して、
        #
        #       ２（Ｘ－１）＋２（ｘー１）＋ｘ
        #
        #   としたものが、［最長対局数］だ。
        #
        #
        #   仮に、Ｘ＝１、ｘ＝１　を式に入れてみる。
        #
        #       ２（１－１）＋２（１ー１）＋１　＝　１
        #
        #   対局数は１と分かる。
        #
        #
        #   ・　Ｘ＝１、ｘ＝１ ----> 最長対局数　１
        #   ・　Ｘ＝２、ｘ＝１ ----> 最長対局数　３
        #   ・　Ｘ＝３、ｘ＝１ ----> 最長対局数　５
        #   ・　Ｘ＝３、ｘ＝２ ----> 最長対局数　７
        #   ・　Ｘ＝４、ｘ＝１ ----> 最長対局数　７
        #   ・　Ｘ＝４、ｘ＝２ ----> 最長対局数　９
        #   ・　Ｘ＝４、ｘ＝３ ----> 最長対局数１１
        #
        #   最長対局数は奇数になるようだ。
        #
        #
        #   'Ａ' を、Ａさんの先手一本、'ａ' を、Ａさんの後手一本、
        #   'Ｂ' を、Ｂさんの先手一本、'ｂ' を、Ｂさんの後手一本とする。
        #
        #
        #   Ｘ＝１、ｘ＝１　最長対局数が１のケースの全パターンを見てみよう
        #
        #   (1) Ａ （先） ----> Ａさんの勝ち
        #   (2) ｂ （後） ----> Ｂさんの勝ち
        #
        #   これだと、Ｂさんは後手しか持てなくて厳しそうだ。 p=0.5 ぐらいの、五分五分ということか？
        #
        #
        #   Ｘ＝２、ｘ＝１　最長対局数が３のケースの全パターンを見てみよう
        #
        #                                           通分 先手は 1 点、後手は 2 点
        #                                           ----------------------------
        #   (1) ＡＢＡ（先先先） ----> Ａさんの勝ち     Ａさん 2 点、Ｂさん 1 点
        #   (2) ＡＢｂ（先先後） ----> Ｂさんの勝ち     Ａさん 1 点、Ｂさん 3 点
        #   (3) Ａａ　（先後　） ----> Ａさんの勝ち     Ａさん 3 点
        #   (4) ｂ　　（後　　） ----> Ｂさんの勝ち     Ｂさん 2 点
        #
        #   Ａさんは先手２回で勝てるのに対し、Ｂさんは後手を含めないと勝てない。
        #
        #   NOTE なんか先手のＡさんが有利なような気がするが、コイン投げ試行をしてみると、印象とはべつに成績としてバランスはとれているようだ？
        #
        #   思考：
        #       以下、偶数対局毎に手番を交代するとしたときの、Ｘ＝２、ｘ＝１　３本勝負のケースの全パターン
        #       
        #       (1) ＡＢＢ（先先先） ----> Ｂさんの勝ち
        #       (2) ＡＢａ（先先後） ----> Ａさんの勝ち
        #       (3) Ａａ　（先後　） ----> Ａさんの勝ち
        #       (4) ｂ　　（後　　） ----> Ｂさんの勝ち
        #       
        #       Ｂさんは先手２回で勝てるのに対し、Ａさんは後手を含めないと勝てない。
        #   
        #   
        #   期待勝利機会という考え方。先手一本も後手一本も 0.5。
        #   後手が２回回ってくるのも、２局１セットで考えれば普通。
        #   先手が先にＡさんに回ってきて、そこで２局１セットでないのが不満感？
        #   第３局で終わりにせず、第４局の消化試合までやるべき？ そしたら引き分けが生まれるのでは？ 引き分けにする権利？
        #
        #   NOTE ［先後固定制］と［先後交互制］で、引き分けにならないかどうかは、変わるだろうか？
        #
        #   FIXME 合ってるか、あとで確認
        #

        is_update = False

        # FIXME ［黒勝ちだけでの対局数］は計算で求めます。 float 型になってしまう？ time を使わず、 step だけでプログラムを書けないか？
        best_b_time = (best_number_of_longest_bout_when_frozen_turn-2*(best_w_time-1))/2

        is_automatic = best_new_p_error >= limit_of_error or best_number_of_longest_bout_when_frozen_turn == 0 or best_round_count < 2_000_000 or best_w_time == 0

        # アルゴリズムで求めるケース
        if is_automatic:

            is_cutoff = False

            # ［最長対局数（先後固定制）］
            for number_of_longest_bout_when_frozen_turn in range(best_number_of_longest_bout_when_frozen_turn, 101):

                # １本勝負のときだけ、白はｎ本－１ではない
                if number_of_longest_bout_when_frozen_turn == 1:
                    end_w_time = 2
                else:
                    end_w_time = number_of_longest_bout_when_frozen_turn

                for w_time in range(1, end_w_time):

                    # FIXME ［黒勝ちだけでの対局数］は計算で求めます。計算合ってる？
                    b_time = number_of_longest_bout_when_frozen_turn-(w_time-1)

                    # ［勝ち点ルール］の構成
                    points_configuration = PointsConfiguration.let_points_from_repeat(b_time, w_time)

                    black_win_count = n_round_when_frozen_turn(
                            p=p,
                            number_of_longest_bout_when_frozen_turn=number_of_longest_bout_when_frozen_turn,
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
                        best_number_of_longest_bout_when_frozen_turn = number_of_longest_bout_when_frozen_turn
                    
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
            print_when_generate_even_when_alternating_turn(p, best_new_p, best_new_p_error, best_round_count, best_points_configuration)

            # データチェック
            if best_points_configuration.let_number_of_longest_bout_when_frozen_turn() != best_number_of_longest_bout_when_frozen_turn:
                raise ValueError(f"実践値と理論値が異なる {best_points_configuration.let_number_of_longest_bout_when_frozen_turn()=}  {best_number_of_longest_bout_when_frozen_turn=}")

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

            # ［最長対局数（先後固定制）］列を更新
            #
            #   FIXME 削除方針。これを使うよりも、 b_step, w_step, span を使った方がシンプルになりそう
            #
            df.loc[df['p']==p, ['number_of_longest_bout_when_frozen_turn']] = best_number_of_longest_bout_when_frozen_turn

            # CSV保存
            df.to_csv(CSV_FILE_PATH,
                    # ［計算過程］列は長くなるので末尾に置きたい
                    columns=['p', 'new_p', 'new_p_error', 'round_count', 'b_step', 'w_step', 'span', 'b_time', 'w_time', 'number_of_longest_bout_when_frozen_turn', 'process'],
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
        df['number_of_longest_bout_when_frozen_turn'].fillna(0).astype('int')
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
