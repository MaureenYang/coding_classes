TITLE = "學生成績排名"
TOPIC = "struct/qsort"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0

import string


def fmt(students, queries):
    s = f"{len(students)}\n" + "".join(f"{n} {sc} {a}\n" for n, sc, a in students)
    return s + f"{len(queries)}\n" + "\n".join(queries)


def rand_names(rng, k, maxlen, alpha):
    names = set()
    while len(names) < k:
        names.add("".join(rng.choice(alpha) for _ in range(rng.randint(1, maxlen))))
    return list(names)


def rand_case(rng, n, q, alpha, maxlen, scores, ages):
    names = rand_names(rng, n + max(1, q // 4), maxlen, alpha)
    students = [(names[i], rng.choice(scores), rng.choice(ages)) for i in range(n)]
    queries = [rng.choice(names) for _ in range(q)]
    return fmt(students, queries)


def manual_cases():
    return [
        ("sample", fmt([("amy", 90, 20), ("bob", 95, 22), ("cat", 90, 19), ("dan", 90, 19)], ["cat", "eve", "bob"])),
        ("single_student", fmt([("solo", 0, 1)], ["solo", "sol", "soloo", "a"])),
        ("no_queries", fmt([("b", 50, 10), ("a", 50, 10)], [])),
        ("all_tied_score_age", fmt([(c, 100, 18) for c in "zyxwvutsrq"], ["q", "z", "m"])),
        ("score_extremes", fmt([("low", 0, 150), ("high", 100, 1), ("mid", 50, 75), ("high2", 100, 150)], ["high2", "low"])),
        ("prefix_names", fmt([("a", 1, 1), ("ab", 1, 1), ("abc", 1, 1), ("b", 1, 1)], ["ab", "abc", "abcd", "aa"])),
        ("long_names", fmt([("a" * 20, 70, 30), ("a" * 19 + "b", 70, 30), ("b" * 20, 71, 30)],
                           ["a" * 20, "a" * 19 + "b", "a" * 21, "b" * 20])),
        ("age_breaks_tie", fmt([("old", 80, 99), ("young", 80, 1), ("mid", 80, 50)], ["young", "old"])),
    ]


def random_case(rng, size):
    if size == "small":
        return rand_case(rng, rng.randint(1, 6), 5, "abc", 3, range(0, 3), range(1, 3))
    if size == "medium":
        return rand_case(rng, 2000, 2000, string.ascii_lowercase, 6, range(0, 101), range(15, 25))
    return rand_case(rng, 100000, 100000, string.ascii_lowercase, 20, range(0, 101), range(1, 151))
