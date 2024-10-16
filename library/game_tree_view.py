class GameTreeView():


    def can_connect_to_parent(prev_gt_record, curr_gt_record, round_th):
        """TODO 前ラウンドにノードがあるか？"""

        prev_round_th = round_th - 1
        prev_round_no = prev_round_th - 1

        # 先頭行は、ラウンド０も含め、全部親ノードに接続できる
        if curr_gt_record.no == 1:
            return True

        try:
            # 前ラウンドは、前行とレートが異なるか？
            return prev_gt_record.node_at(prev_round_no).rate != curr_gt_record.node_at(prev_round_no).rate

        # AttributeError: 'NoneType' object has no attribute 'rate'
        except AttributeError as e:
            raise AttributeError(f"{round_th=}  {prev_round_no=}  {prev_gt_record.node_at(prev_round_no)=}  {curr_gt_record.node_at(prev_round_no)=}") from e

        # IndexError: round_th=9  prev_round_no=7  prev_gt_record.len_node_list=6  curr_gt_record.len_node_list=6
        except IndexError as e:
            raise IndexError(f"{round_th=}  {prev_round_no=}  {prev_gt_record.len_node_list=}  {curr_gt_record.len_node_list=}") from e
