"""
1000x1000 Cross/X MAC experiment:
- 2D full-array calculation
- 1D flattened full-array calculation (Bonus 1)
- 2D row-by-row streaming
- 1D row-by-row streaming (row buffer + flattened filters)

Run:
    python large_scale_1d_test.py

Timing notes:
- Full-array methods use patterns generated before timing.
- Row-streaming methods generate each input row during the timed calculation.
- Each method is measured 7 times; the median is displayed.
"""

import statistics
import time

SIZE = 1000
REPEATS = 7


def bit_at(kind, row, col, size):
    """Return one cell of a Cross or X pattern."""
    if kind == "cross":
        center_rows = (size // 2 - 1, size // 2)
        return int(row in center_rows or col in center_rows)

    return int(row == col or row + col == size - 1)


def make_2d(kind, size):
    """Create a pattern as a two-dimensional list."""
    return [
        [bit_at(kind, row, col, size) for col in range(size)]
        for row in range(size)
    ]


def make_1d(kind, size):
    """Create the same pattern as a flattened one-dimensional list."""
    return [
        bit_at(kind, index // size, index % size, size)
        for index in range(size * size)
    ]


def mac_2d(pattern, filter_data):
    """MAC using 2D row/column indexing."""
    score = 0

    for row in range(len(pattern)):
        for col in range(len(pattern[row])):
            score += pattern[row][col] * filter_data[row][col]

    return score


def mac_1d(pattern_flat, filter_flat):
    """MAC using one flattened index, as in Bonus 1."""
    score = 0

    for index in range(len(pattern_flat)):
        score += pattern_flat[index] * filter_flat[index]

    return score


def mac_row_stream_2d(kind, cross_filter, x_filter, size):
    """Generate one input row at a time and access filters as 2D lists."""
    cross_score = 0
    x_score = 0

    for row_index in range(size):
        input_row = [
            bit_at(kind, row_index, col, size)
            for col in range(size)
        ]

        for col in range(size):
            value = input_row[col]
            cross_score += value * cross_filter[row_index][col]
            x_score += value * x_filter[row_index][col]

    return cross_score, x_score


def mac_row_stream_1d(kind, cross_filter_flat, x_filter_flat, size):
    """
    Generate one 1D input row at a time.
    Access flattened filters with index = row_index * size + col.
    """
    cross_score = 0
    x_score = 0

    for row_index in range(size):
        input_row = [
            bit_at(kind, row_index, col, size)
            for col in range(size)
        ]

        row_start = row_index * size

        for col in range(size):
            flat_index = row_start + col
            value = input_row[col]
            cross_score += value * cross_filter_flat[flat_index]
            x_score += value * x_filter_flat[flat_index]

    return cross_score, x_score


def measure(function, kind, repeats=REPEATS):
    """Return the result and median/mean elapsed time."""
    samples = []
    result = None

    for _ in range(repeats):
        start = time.perf_counter()
        result = function(kind)
        samples.append(time.perf_counter() - start)

    return result, statistics.median(samples), statistics.mean(samples)


def main():
    print(f"Array size: {SIZE} x {SIZE}")
    print(f"Number of cells: {SIZE * SIZE:,}")
    print(f"Timing repetitions: {REPEATS}")
    print()

    # Prepare full arrays before timing the full-array MAC functions.
    start = time.perf_counter()
    cross_2d = make_2d("cross", SIZE)
    x_2d = make_2d("x", SIZE)
    generation_2d = time.perf_counter() - start

    start = time.perf_counter()
    cross_flat = make_1d("cross", SIZE)
    x_flat = make_1d("x", SIZE)
    generation_1d = time.perf_counter() - start

    # Filters are also prepared before calculation timing.
    cross_filter_2d = make_2d("cross", SIZE)
    x_filter_2d = make_2d("x", SIZE)
    cross_filter_flat = make_1d("cross", SIZE)
    x_filter_flat = make_1d("x", SIZE)

    def run_2d_full(kind):
        pattern = cross_2d if kind == "cross" else x_2d
        return (
            mac_2d(pattern, cross_filter_2d),
            mac_2d(pattern, x_filter_2d),
        )

    def run_1d_full(kind):
        pattern = cross_flat if kind == "cross" else x_flat
        return (
            mac_1d(pattern, cross_filter_flat),
            mac_1d(pattern, x_filter_flat),
        )

    def run_2d_row_stream(kind):
        return mac_row_stream_2d(
            kind, cross_filter_2d, x_filter_2d, SIZE
        )

    def run_1d_row_stream(kind):
        return mac_row_stream_1d(
            kind, cross_filter_flat, x_filter_flat, SIZE
        )

    methods = {
        "2D full": run_2d_full,
        "1D full": run_1d_full,
        "2D row-stream": run_2d_row_stream,
        "1D row-stream": run_1d_row_stream,
    }

    expected = {
        "cross": (4 * SIZE - 4, 4),
        "x": (4, 2 * SIZE),
    }

    print("[Pattern generation time]")
    print(f"2D input patterns: {generation_2d:.6f} sec")
    print(f"1D input patterns: {generation_1d:.6f} sec")
    print()

    all_passed = True

    for kind in ("cross", "x"):
        print(f"[{kind.upper()} input]")
        baseline_result = None

        for method_name, function in methods.items():
            result, median_time, mean_time = measure(function, kind)

            if baseline_result is None:
                baseline_result = result

            passed = result == expected[kind] and result == baseline_result
            all_passed = all_passed and passed
            status = "PASS" if passed else "FAIL"

            print(
                f"{method_name:16} "
                f"Cross={result[0]:.0f}, X={result[1]:.0f} | "
                f"median={median_time:.6f} sec | "
                f"mean={mean_time:.6f} sec | {status}"
            )

        print()

    print("[Final result]")
    print(
        "PASS: all methods produced the expected, identical scores."
        if all_passed
        else "FAIL: at least one method produced an unexpected result."
    )

    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
