
import json
import math

EPSILON = 1e-9

CROSS_3 = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0]
]

X_3 = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
]


def mac(pattern, filter_data):
    score = 0.0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score


def decide(score_a, score_b, label_a="A", label_b="B"):
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    return label_a if score_a > score_b else label_b


def input_matrix(name):
    print(f"\n{name} 입력")
    print("각 줄마다 숫자 공백 숫자 공백 숫자 순서로 입력하고 Enter를 누르세요.")

    matrix = []

    while len(matrix) < 3:
        print(f"{len(matrix) + 1}번째 줄 입력 (예: 0 1 0): ", end="")

        try:
            row = [float(value) for value in input().split()]

            if len(row) != 3 or not all(math.isfinite(v) for v in row):
                print("입력 오류: 숫자 3개를 정확히 입력하세요.")
                continue

            matrix.append(row)

        except ValueError:
            print("입력 오류: 숫자만 입력하세요.")

    return matrix


def manual_mode():
    pattern = input_matrix("패턴")

    score_cross = mac(pattern, CROSS_3)
    score_x = mac(pattern, X_3)

    result = decide(score_cross, score_x, "Cross", "X")

    print("\n[계산 결과]")
    print("Cross 점수:", score_cross)
    print("X 점수:", score_x)
    print("최종 판정:", result)


def load_data(filename="data.json"):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


# JSON 데이터 자동 분석
def json_mode(data):
    filters = data["filters"]
    patterns = data["patterns"]

    passed = 0
    failed = 0

    for case_id, case in patterns.items():
        print(f"\n--- {case_id} ---")

        parts = case_id.split("_")
        size = int(parts[1])

        filter_key = f"size_{size}"
        group = filters[filter_key]

        pattern = case["input"]
        expected = "Cross" if case["expected"] == "+" else "X"

        cross_filter = group["cross"]
        x_filter = group["x"]

        cross_score = mac(pattern, cross_filter)
        x_score = mac(pattern, x_filter)

        result = decide(cross_score, x_score, "Cross", "X")

        if result == expected:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print(f"Cross 점수: {cross_score:.3f}")
        print(f"X 점수: {x_score:.3f}")
        print(f"판정: {result} | 정답: {expected} | {status}")

    print("\n[최종 결과]")
    print(f"총 테스트: {len(patterns)}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")


data = load_data()
json_mode(data)
