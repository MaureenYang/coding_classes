TITLE = "迷宮最短路徑"
TOPIC = "Graph/BFS"
DIFFICULTY = "★★☆"
TIME_LIMIT = 2.0


def fmt(grid):
    return f"{len(grid)} {len(grid[0])}\n" + "\n".join(grid)


def place(grid, rng):
    """在空地隨機放 S 和 T"""
    g = [list(r) for r in grid]
    free = [(r, c) for r in range(len(g)) for c in range(len(g[0])) if g[r][c] == '.']
    (sr, sc), (tr, tc) = rng.sample(free, 2)
    g[sr][sc], g[tr][tc] = 'S', 'T'
    return ["".join(r) for r in g]


def serpentine(R, C):
    """蛇形迷宮：一條唯一的長路，S 在左上，T 在路的盡頭"""
    g = []
    for r in range(R):
        if r % 2 == 0:
            g.append("." * C)
        elif r % 4 == 1:
            g.append("#" * (C - 1) + ".")
        else:
            g.append("." + "#" * (C - 1))
    g = [list(row) for row in g]
    g[0][0] = 'S'
    last = R - 1 if R % 2 == 1 else R - 2
    g[last][C - 1 if (last // 2) % 2 == 0 else 0] = 'T'
    return ["".join(row) for row in g]


def manual_cases():
    open_big = ["S" + "." * 999] + ["." * 1000] * 998 + ["." * 999 + "T"]
    return [
        ("sample", fmt(["S.#.", ".##T", "...."])),
        ("1x2_adjacent", fmt(["ST"])),
        ("2x1_vertical", fmt(["T", "S"])),
        ("start_walled_in", fmt(["#.#", "#S#", "###", "..T"])),
        ("target_walled_in", fmt(["S....", "..###", "..#T#", "..###"])),
        ("single_row_long", fmt(["S" + "." * 998 + "T"])),
        ("open_1000x1000", fmt(open_big)),
        ("serpentine_1000x1000", fmt(serpentine(1000, 1000))),
        ("serpentine_999x1000", fmt(serpentine(999, 1000))),
    ]


def random_case(rng, size):
    R, C = {"small": (rng.randint(1, 5), rng.randint(2, 6)),
            "medium": (rng.randint(20, 60), rng.randint(20, 60))}.get(size, (1000, 1000))
    wall = rng.uniform(0.1, 0.45)
    grid = ["".join('#' if rng.random() < wall else '.' for _ in range(C)) for _ in range(R)]
    if sum(row.count('.') for row in grid) < 2:
        grid = ["." * C for _ in range(R)]
    return fmt(place(grid, rng))
