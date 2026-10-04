TITLE = "N 皇后"
TOPIC = "回溯法"
DIFFICULTY = "★★☆"
TIME_LIMIT = 2.0
RANDOM_PLAN = [("small", 3)]


def manual_cases():
    # n 只有 13 種，全部都測
    names = {1: "n1_trivial", 2: "n2_no_solution", 3: "n3_no_solution", 4: "n4_sample", 13: "n13_max"}
    return [(names.get(n, f"n{n}"), str(n)) for n in range(1, 14)]


def random_case(rng, size):
    return str(rng.randint(1, 10))
