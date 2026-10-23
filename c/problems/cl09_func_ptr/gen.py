TITLE = "函式指標與指令表"
TOPIC = "函式指標"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

MAPS = ["neg", "abs", "half", "inc", "dec", "mod10"]
PREDS = ["even", "odd", "pos", "neg", "nonzero"]
FOLDS = ["sum", "count", "prodmod", "max", "min"]
CMPS = ["asc", "desc", "absasc"]
UNKNOWN = ["sqrt", "square", "Neg", "ascending", "sum2", "x"]


def fmt(arr, ops):
    return f"{len(arr)}\n{' '.join(map(str, arr))}\n{len(ops)}\n" + "\n".join(ops)


def rand_ops(rng, q, n, print_ok):
    ops = []
    incs = 0
    for _ in range(q):
        k = rng.randrange(5)
        bad = rng.random() < 0.08
        if k == 0:
            f = rng.choice(UNKNOWN) if bad else rng.choice(MAPS)
            if f in ("inc", "dec"):
                if incs >= 50000: f = "half"
                incs += 1
            ops.append(f"map {f}")
        elif k == 1:
            ops.append(f"filter {rng.choice(UNKNOWN) if bad else rng.choice(PREDS)}")
        elif k == 2:
            ops.append(f"reduce {rng.choice(UNKNOWN) if bad else rng.choice(FOLDS)}")
        elif k == 3:
            ops.append(f"sort {rng.choice(UNKNOWN) if bad else rng.choice(CMPS)}")
        else:
            ops.append("print" if print_ok else "reduce sum")
    return ops


def manual_cases():
    return [
        ("sample", fmt([3, -8, 5, 0, -2], ["map half", "print", "filter nonzero", "reduce prodmod", "sort absasc", "print", "map sqrt", "reduce max"])),
        ("negative_division_and_mod", fmt([-7, 7, -1, 1, -15, 15], ["map half", "print", "map mod10", "print"])),
        ("negative_odd", fmt([-3, -2, -1, 0, 1, 2, 3], ["filter odd", "print", "reduce count"])),
        ("filter_to_empty", fmt([1, 2, 3], ["filter neg", "print", "reduce sum", "reduce count", "reduce prodmod", "reduce max",
                                            "reduce min", "map neg", "sort desc", "print", "filter pos", "print"])),
        ("prodmod_negative", fmt([-1, 1000000000, -1000000000, 7], ["reduce prodmod", "map neg", "reduce prodmod"])),
        ("absasc_ties", fmt([3, -3, 0, -1, 1, 2, -2, 0], ["sort absasc", "print", "sort desc", "print", "sort asc", "print"])),
        ("extreme_compare", fmt([2000000000, -2000000000, 1999999999, -1999999999, 1000000000], ["sort asc", "print", "sort desc", "print",
                                                                                   "sort absasc", "print", "reduce sum"])),
        ("compare_overflow", fmt([-2000000000, 2000000000, -2000000000, 2000000000, 0, 1999999999],
                                 ["sort asc", "print", "sort desc", "print", "sort absasc", "print"])),
        ("unknown_names", fmt([5], ["map sqrt", "filter big", "reduce avg", "sort random", "map NEG", "print"])),
        ("same_name_different_table", fmt([-5, 5], ["filter neg", "print", "map neg", "print"])),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 6), "medium": 500}.get(size, 10000)
    q = {"small": 8, "medium": 300}.get(size, 1000)
    lim = {"small": 20}.get(size, 2 * 10 ** 9)
    arr = [rng.randint(-lim, lim) for _ in range(n)]
    return fmt(arr, rand_ops(rng, q, n, size != "large"))
