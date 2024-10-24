from library import IN_GAME, ALICE_FULLY_WON, BOB_FULLY_WON, ALICE_POINTS_WON, BOB_POINTS_WON, NO_WIN_MATCH
from library.database import GameTreeNode, GameTreeRecord
from library.views import ScoreBoardViewData


class Automatic():


    def __init__(self, spec, gt_table):
        self._spec = spec
        self._gt_table = gt_table


    def on_score_board_created(self, score_board):


        no = score_board.pattern_no


        if score_board.game_results == IN_GAME:
            raise ValueError(f"対局中なのはおかしい")
        
        elif score_board.game_results == ALICE_FULLY_WON:
            result = "達成でＡさんの勝ち"

        elif score_board.game_results == BOB_FULLY_WON:
            result = "達成でＢさんの勝ち"

        elif score_board.game_results == ALICE_POINTS_WON:
            result = "勝ち点差でＡさんの勝ち"

        elif score_board.game_results == BOB_POINTS_WON:
            result = "勝ち点差でＢさんの勝ち"
        
        elif score_board.game_results == NO_WIN_MATCH:
            result = "勝者なし"

        else:
            raise ValueError(f"{score_board.game_results=}")
        


        # score board view data
        V = ScoreBoardViewData.from_data(score_board)

        a_span = int(V.path_of_a_count_down_points_str[1])
        b_span = int(V.path_of_b_count_down_points_str[1])
        a_pts = a_span
        b_pts = b_span

        # [0], [1] は見出しデータ
        MIDASI = 2
        number_of_round = len(V.path_of_round_number_str) - MIDASI

        face_list = []
        winner_list = []
        pts_list = []
        rate_list = []

        pattern_rate = 1
        successful_p = (1 - self._spec.failure_rate) * self._spec.p
        successful_q = (1 - self._spec.failure_rate) * (1 - self._spec.p)

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
                winner_list.append('N')
                pts_list.append(-1)

            else:
                # カウントダウン式で記録されているので、カウントアップ式に変換する
                if player_name == 'A':
                    pts = a_span - a_pts
                elif player_name == 'B':
                    pts = b_span - b_pts
                else:
                    raise ValueError(f'{player_name=}')

                winner_list.append(player_name)
                pts_list.append(pts)


            # 確率計算
            if face_of_coin == '表':
                face_list.append('h')
                pattern_rate *= successful_p
            elif face_of_coin == '裏':
                face_list.append('t')
                pattern_rate *= successful_q
            elif player_name == '失':
                face_list.append('f')
                pattern_rate *= self._spec.failure_rate
            else:
                raise ValueError(f'{player_name=}')


            rate_list.append(pattern_rate)


        node_list = []

        for i in range(0, 6):
            if i < number_of_round:
                edge_text = GameTreeNode.get_edge_text(face=face_list[i], winner=winner_list[i], pts=pts_list[i])
                text = rate_list[i]
                node_list.append(GameTreeNode(edge_text=edge_text, text=text, face=face_list[i], winner=winner_list[i], pts=pts_list[i], rate=rate_list[i]))
            else:
                node_list.append(GameTreeNode(edge_text=None, text=None, face=None, winner=None, pts=None, rate=None))


        self._gt_table.upsert_record(
                welcome_record=GameTreeRecord(
                        no=no,
                        result=result,
                        node_list=node_list))
