class GameTreeView():


    def can_connect_to_parent(prev_gt_record, curr_gt_record, round_th):
        """TODO 前ラウンドにノードがあるか？"""

        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        # 先頭行だけ、ラウンド０に接続できる
        if prev_round_no == -1:
            return curr_gt_record.no == 1

        try:
            return prev_gt_record.node_at(prev_round_no) != curr_gt_record.node_at(prev_round_no)
        
        except IndexError as e:
            raise IndexError(f"{round_th=}  {prev_round_no=}  {prev_gt_record.len_node_list=}  {curr_gt_record.len_node_list=}") from e
