from library import FROZEN_TURN, Specification
from library_for_game import GamePlan


# 明瞭にフェアー
exactly_fair_list_of_game_plan = [
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.5),
            span=1,
            t_step=1,
            h_step=1,
            a_victory_rate=0.5,
            b_victory_rate=0.5,
            no_victory_rate=0.0),
]

# フェアー
fair_list_of_game_plan = [
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.61),
            span=3,
            t_step=2,
            h_step=1,
            a_victory_rate=0.49254877,
            b_victory_rate=0.50745123,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.69),
            span=2,
            t_step=2,
            h_step=1,
            a_victory_rate=0.476099999999999,
            b_victory_rate=0.5239,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.7),
            span=2,
            t_step=2,
            h_step=1,
            a_victory_rate=0.49,
            b_victory_rate=0.51,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.74),
            span=10,
            t_step=5,
            h_step=2,
            a_victory_rate=0.510371523519999,
            b_victory_rate=0.489628476479999,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.76),
            span=9,
            t_step=4,
            h_step=1,
            a_victory_rate=0.486565383405516,
            b_victory_rate=0.513434616594476,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.82),
            span=15,
            t_step=14,
            h_step=2,
            a_victory_rate=0.498770369511813,
            b_victory_rate=0.501229630488185,
            no_victory_rate=0.0),
]


# 明瞭にアンフェア
exactly_unfair_list_of_game_plan = [
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.7),
            span=1,
            t_step=1,
            h_step=1,
            a_victory_rate=0.7,
            b_victory_rate=0.3,
            no_victory_rate=0.0)
]


# アンフェア
unfair_list_of_game_plan = [
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.55),
            span=4,
            t_step=3,
            h_step=1,
            a_victory_rate=0.2562175,
            b_victory_rate=0.743782499999999,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.57),
            span=3,
            t_step=2,
            h_step=1,
            a_victory_rate=0.424091969999999,
            b_victory_rate=0.57590803,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.6),
            span=2,
            t_step=2,
            h_step=1,
            a_victory_rate=0.36,
            b_victory_rate=0.64,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.65),
            span=3,
            t_step=2,
            h_step=1,
            a_victory_rate=0.562981249999999,
            b_victory_rate=0.437018749999999,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.7),
            span=3,
            t_step=3,
            h_step=1,
            a_victory_rate=0.342999999999999,
            b_victory_rate=0.657,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.75),
            span=3,     # 9
            t_step=2,   # 6
            h_step=1,   # 3
            a_victory_rate=0.73828125,
            b_victory_rate=0.26171875,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.77),
            span=3,     # 11
            t_step=3,   # 11
            h_step=1,   # 5
            a_victory_rate=0.456533,
            b_victory_rate=0.543466999999999,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.81),
            span=6,
            t_step=4,
            h_step=1,
            a_victory_rate=0.60439920806934,
            b_victory_rate=0.395600791930657,
            no_victory_rate=0.0),
    GamePlan(
            spec=Specification.by_three_rates(
                    turn_system_id=FROZEN_TURN,
                    failure_rate=0.0,
                    head_rate=0.90),
            span=4,
            t_step=4,
            h_step=1,
            a_victory_rate=0.6561,
            b_victory_rate=0.343899999999999,
            no_victory_rate=0.0),
]
