from library import IN_GAME, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH
from library.database import GameTreeNode, GameTreeRecord
from library.views import ScoreBoardViewData


class Automatic():
    """スコアボードの結果を、ツリー構造表示に使えるCSV形式に変換します
    TODO step_oa41o0_gt.py から移行中
    """


    def __init__(self, spec, root_entry):
        self._spec = spec
        self._root_entry = root_entry


    def on_score_board_created(self, score_board):

        # score board view data
        V = ScoreBoardViewData.from_data(score_board)

        a_span = int(V.path_of_a_count_down_points_str[1])
        b_span = int(V.path_of_b_count_down_points_str[1])
        a_pts = a_span
        b_pts = b_span

        # [0], [1] は見出しデータ
        MIDASI = 2
        number_of_round = len(V.path_of_round_number_str) - MIDASI

        pattern_rate = 1
        successful_p = (1 - self._spec.failure_rate) * self._spec.p
        successful_q = (1 - self._spec.failure_rate) * (1 - self._spec.p)


        cur_entry = self._root_entry

        for i in range(0, number_of_round):
            prev_a_pts = int(V.path_of_a_count_down_points_str[i + MIDASI - 1])
            prev_b_pts = int(V.path_of_b_count_down_points_str[i + MIDASI - 1])
            a_pts = int(V.path_of_a_count_down_points_str[i + MIDASI])
            b_pts = int(V.path_of_b_count_down_points_str[i + MIDASI])


            # FIXME どちらが勝ったかの判定は、カウントが減っているかで判定
            if a_pts < prev_a_pts and b_pts < prev_b_pts:
                raise ValueError(f'両者のポイントが変わっているのはおかしい  {prev_a_pts=}  {prev_b_pts=}  {a_pts=}  {b_pts=}')
            elif a_pts < prev_a_pts:
                player_name = 'A'
            elif b_pts < prev_b_pts:
                player_name = 'B'
            else:
                player_name = '失'


            face_of_coin = V.path_of_face_of_coin_str[i + MIDASI]


            # ［失敗］表記
            if player_name == '失':
                winner = 'N'
                pts = -1

            else:
                # カウントダウン式で記録されているので、カウントアップ式に変換する
                if player_name == 'A':
                    pts = a_span - a_pts
                elif player_name == 'B':
                    pts = b_span - b_pts
                else:
                    raise ValueError(f'{player_name=}')

                winner = player_name


            # 確率計算
            if face_of_coin == '表':
                face = 'h'
                pattern_rate *= successful_p
            elif face_of_coin == '裏':
                face = 't'
                pattern_rate *= successful_q
            elif player_name == '失':
                face = 'f'
                pattern_rate *= self._spec.failure_rate
            else:
                raise ValueError(f'{player_name=}')


            et = GameTreeNode.get_edge_text(face=face, winner=winner, pts=pts)
            nt = pattern_rate

#             print(f"""({i}) デバッグ：
# {cur_entry.edge_text=}
# {cur_entry.node_text=}
# {cur_entry._stringify_like_tree('')}""")

            # 子要素が既存なら、それを取得する。無ければ grow する
            child_entry = cur_entry.get_child(edge_text=et, node_text=nt)
            if child_entry is not None:
                cur_entry = child_entry
            else:
                cur_entry = cur_entry.grow(
                        edge_text=et,
                        node_text=nt)


        def get_result(game_results):
            if game_results == IN_GAME:
                raise ValueError(f"対局中なのはおかしい")
            
            if game_results == ALICE_FULLY_WON:
                return "達成でＡさんの勝ち"

            if game_results == BOB_FULLY_WON:
                return "達成でＢさんの勝ち"

            if game_results == ALICE_POINTS_WON:
                return "勝ち点差でＡさんの勝ち"

            if game_results == BOB_POINTS_WON:
                return "勝ち点差でＢさんの勝ち"
            
            if game_results == NO_WIN_MATCH:
                return "勝者なし"

            raise ValueError(f"{score_board.game_results=}")


        # 最後は葉
        cur_entry.leaf_th = score_board.pattern_no
        cur_entry.remainder_columns = {
            'result':get_result(game_results=score_board.game_results),
        }
