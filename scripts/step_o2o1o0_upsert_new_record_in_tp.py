import datetime
import pandas as pd

from library import OUT_OF_P, Converter, SeriesRule, round_letro
from library.database import TheoreticalProbabilityRecord, TheoreticalProbabilityTable


class Automation():
    """［理論的確率データ］（TP）表に新規行を挿入する。

    FIXME 更新するつもりはないが、既存行が一斉に同じレコードになるような不具合が起こる
    アップサートにしても解決しない
    NOTE 主キーや、ロック機構がないので、インデックスが重複するようなレコードを追加できてしまう？
    """


    def execute(self, spec, tp_table, is_tp_file_created, upper_limit_span):
        """［理論的確率データ］の新規行を挿入する"""
        number_of_dirty = 0

        # ループカウンター
        if len(tp_table._df) < 1:
            span = 1        # ［目標の点数］
            t_step = 1      # ［後手で勝ったときの勝ち点］
            h_step = 1      # ［先手で勝ったときの勝ち点］

        else:
            # 途中まで処理が終わってるんだったら、途中から再開したいが。ループの途中から始められるか？

            #
            # NOTE 4.999...9997 みたいな数が入ってたら int() で 4 に切り下げられるの嫌なので、 round_letro() を使う
            #

            # FIXME ここもっと簡潔に書けそう？
            # TODO 最後に処理された span は？
            span = round_letro(tp_table._df['span'].max())

            # TODO 最後に処理された span のうち、最後に処理された t_step は？
            t_step = round_letro(tp_table._df.loc[tp_table._df['span']==span, 't_step'].max())

            # TODO 最後に処理された span, t_step のうち、最後に処理された h_step は？
            h_step = round_letro(tp_table._df.loc[(tp_table._df['span']==span) & (tp_table._df['t_step']==t_step), 'h_step'].max())

            # カウントアップ
            span, t_step, h_step = Automation.increase(span, t_step, h_step)

            print(f"{datetime.datetime.now()}RESTART_ {span=:2}  {t_step=:2}  {h_step=:2}")


        #
        # TODO ロック機構がないと、データの整合性が取れないのでは？
        #
        while span < upper_limit_span + 1:

#             # 該当レコードのキー
#             #
#             #   <class 'pandas.core.series.Series'>
#             #   各行について True, False の論理値を付けたシリーズ
#             #
#             list_of_enable_each_row = (tp_table._df['span']==span) & (tp_table._df['t_step']==t_step) & (tp_table._df['h_step']==h_step)
# #                         print(f"""\
# # {type(list_of_enable_each_row)=}
# # {list_of_enable_each_row=}""")

            # インデックス
            result_set_df_by_index = tp_table.get_result_set_by_index(
                    span=span,
                    t_step=t_step,
                    h_step=h_step)
            
            if 1 < len(result_set_df_by_index):
                raise ValueError(f"テーブルが壊れています。インデックスが重複するデータが {len(result_set_df_by_index)} 件ありました")

            if len(result_set_df_by_index) == 1:
                raise ValueError(f"プログラムが壊れています。指定した新しいインデックスが既に存在します")


            # # 該当データが１つも無いなら、新規追加
            # #
            # #   TODO データが飛び番とか無ければ、必ずデータは無いはずだが。一応確認しておく？
            # #
            # is_new = not list_of_enable_each_row.any()
            # if is_new:
            #if len(result_set_df_by_index) < 1:

            # ［シリーズ・ルール］
            #
            #   ［最短対局数］と［上限対局数］を求めるのに使う
            #
            specified_series_rule = SeriesRule.make_series_rule_base(
                    spec=spec,
                    span=span,
                    t_step=t_step,
                    h_step=h_step)

            # レコードの挿入
            tp_table.upsert_record(
                    result_set_df_by_index=result_set_df_by_index,
                    welcome_record=TheoreticalProbabilityRecord(
                            span=span,
                            t_step=t_step,
                            h_step=h_step,
                            shortest_coins=specified_series_rule.shortest_coins,
                            upper_limit_coins=specified_series_rule.upper_limit_coins,

                            # NOTE スリー・レーツを求める処理は重たいので、後回しにする
                            theoretical_a_win_rate=OUT_OF_P,
                            theoretical_no_win_match_rate=OUT_OF_P))
            
            number_of_dirty += 1


            # カウントアップ
            span, t_step, h_step = Automation.increase(span, t_step, h_step)


        return number_of_dirty


    @staticmethod
    def increase(span, t_step, h_step):
        """カウントアップ"""
        h_step += 1
        if t_step < h_step:
            h_step = 1
            t_step += 1
            if span < t_step:
                t_step = 1
                span += 1

        return span, t_step, h_step