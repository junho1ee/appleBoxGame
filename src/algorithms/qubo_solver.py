import numpy as np
import dimod
from itertools import product
from typing import List, Tuple

from src.models.box import Box, Strategy
import src.config as config


def solve_fruit_box_with_qubo(grid: List[List[int]]) -> Strategy:
    """
    Find the best strategy using QUBO algorithm.
    """
    # 1. 가능한 모든 박스(합이 10인) 찾기
    possible_boxes = find_boxes_with_sum_10(grid)

    # 2. QUBO 행렬 구성
    n_boxes = len(possible_boxes)
    Q = np.zeros((n_boxes, n_boxes))

    # 목적 함수: 사과 수 최대화 (최소화를 위해 음수 사용)
    for i, (x, y, w, h, count) in enumerate(possible_boxes):
        Q[i, i] = -count  # 대각 요소

    # 제약 조건: 사과는 한 번만 사용
    P = max(abs(Q[i, i]) for i in range(n_boxes)) * 10  # 페널티 상수

    # 각 사과 위치에 대해 그것을 포함하는 모든 박스 쌍 간의 페널티 추가
    for r in range(config.HEIGHT):
        for c in range(config.WIDTH):
            if grid[r][c] > 0:  # 사과가 있는 위치만 고려
                boxes_covering_apple = []
                for i, (x, y, w, h, _) in enumerate(possible_boxes):
                    if x <= c < x + w and y <= r < y + h:
                        boxes_covering_apple.append(i)

                # 같은 사과를 포함하는 모든 박스 쌍에 페널티 추가
                for i in range(len(boxes_covering_apple)):
                    for j in range(i + 1, len(boxes_covering_apple)):
                        idx1, idx2 = boxes_covering_apple[i], boxes_covering_apple[j]
                        Q[idx1, idx2] += P
                        Q[idx2, idx1] += P

    # 3. QUBO 문제 풀기
    sampler = dimod.SimulatedAnnealingSampler()
    response = sampler.sample_qubo(Q, num_reads=1000)

    # 4. 최적 해 추출
    best_solution = response.first.sample
    selected_boxes = [
        possible_boxes[i] for i in range(n_boxes) if best_solution[i] == 1
    ]

    # 선택된 박스들로 전략 생성
    strategy = Strategy(
        boxes=[Box(x=x, y=y, width=w, height=h) for x, y, w, h, _ in selected_boxes],
        score=sum(count for _, _, _, _, count in selected_boxes),
    )

    return strategy


def find_boxes_with_sum_10(grid: List[List[int]]) -> List[Tuple[int, int, int, int, int]]:
    """
    Find all possible boxes with sum 10.
    Returns list of tuples (x, y, width, height, count) where count is number of non-zero cells.
    """
    # 누적합 계산
    np_grid = np.array(grid, dtype=np.int32)
    cum_sum = np.zeros((config.HEIGHT + 1, config.WIDTH + 1), dtype=np.int32)
    cum_sum[1:, 1:] = np.cumsum(np.cumsum(np_grid, axis=0), axis=1)

    # 합이 10인 모든 박스 찾기
    possible_boxes = []
    for y, x in product(range(config.HEIGHT), range(config.WIDTH)):
        for h, w in product(range(1, config.HEIGHT - y + 1), range(1, config.WIDTH - x + 1)):
            box_sum = (
                cum_sum[y + h][x + w]
                - cum_sum[y + h][x]
                - cum_sum[y][x + w]
                + cum_sum[y][x]
            )

            if box_sum == 10:
                count = np.sum(np_grid[y : y + h, x : x + w] > 0)
                possible_boxes.append((x, y, w, h, count))

    return possible_boxes 