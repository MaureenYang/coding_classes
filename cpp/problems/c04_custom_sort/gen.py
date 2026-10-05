TITLE = "多條件排序"
TOPIC = "函式/lambda"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

import string


def fmt(students, queries):
    s = f"{len(students)}\n" + "\n".join(f"{a} {b} {c}" for a, b, c in students)
    return s + f"\n{len(queries)}\n" + "\n".join(f"rank {q}" for q in queries)


def rname(rng, pool):
    return "".join(rng.choice(pool) for _ in range(rng.randint(1, 4)))


def manual_cases():
    return [
        ("sample", fmt([("amy", 90, 20), ("Bob", 95, 22), ("cat", 90, 19), ("amy", 90, 20)], ["amy", "dog"])),
        ("single", fmt([("x", 0, 0)], ["x", "X"])),
        ("uppercase_before_lowercase", fmt([("b", 1, 1), ("B", 1, 1), ("a", 1, 1), ("A", 1, 1), ("ab", 1, 1), ("aB", 1, 1)],
                                           ["a", "A", "aB"])),
        ("negative_scores", fmt([("p", -1000000000, 5), ("q", 1000000000, 5), ("r", 0, 5), ("s", -1, 5)], ["p", "q"])),
        ("duplicate_names_first_occurrence", fmt([("amy", 10, 1), ("amy", 99, 1), ("amy", 50, 1)], ["amy"])),
        ("no_queries", fmt([("a", 1, 2), ("b", 1, 1)], [])),
        ("all_identical_200000", fmt([("same", 7, 7)] * 200000, ["same", "diff"])),
        ("many_ties_strict_weak_ordering", fmt([("a" if i % 2 else "b", i % 3, i % 2) for i in range(200000)],
                                               ["a", "b", "c"] * 1000)),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 8), "medium": 2000}.get(size, 200000)
    pool = "aAbB" if size == "small" else string.ascii_letters
    sc = 3 if size == "small" else 10 ** 9
    students = [(rname(rng, pool), rng.randint(-sc, sc), rng.randint(0, 3 if size == "small" else 150)) for _ in range(n)]
    names = [s[0] for s in students]
    q = {"small": 5, "medium": 2000}.get(size, 200000)
    queries = [rng.choice(names) if rng.random() < 0.8 else rname(rng, pool) for _ in range(q)]
    return fmt(students, queries)
