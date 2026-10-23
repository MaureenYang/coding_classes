TITLE = "用指標操作陣列"
TOPIC = "指標參數"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0


def fmt(arr, ops):
    return f"{len(arr)}\n{' '.join(map(str, arr))}\n{len(ops)}\n" + "\n".join(ops)


def rand_ops(rng, n, q, vals):
    ops = []
    for _ in range(q):
        k = rng.randrange(6)
        l = rng.randrange(n); r = rng.randrange(l, n)
        if k == 0:
            i = rng.randrange(n)
            ops.append(f"swap {i} {i if rng.random() < 0.2 else rng.randrange(n)}")
        elif k == 1:
            ops.append(f"minmax {l} {r}")
        elif k == 2:
            ops.append(f"rev {l} {r}")
        elif k == 3:
            ops.append(f"find {rng.choice(vals) if rng.random() < 0.7 else rng.randint(-10 ** 9, 10 ** 9)}")
        elif k == 4:
            ops.append(f"rot {rng.choice([0, n, rng.randint(0, 2 * n), rng.randint(0, 10 ** 9)])}")
        else:
            ops.append("print")
    return ops


def manual_cases():
    return [
        ("sample", fmt([3, 1, 4, 1, 5], ["minmax 0 4", "find 1", "rev 1 3", "print", "rot 2", "print", "find 9"])),
        ("n1_everything", fmt([7], ["swap 0 0", "minmax 0 0", "rev 0 0", "find 7", "find 8", "rot 0", "rot 1000000000", "print"])),
        ("swap_self", fmt([1, 2, 3], ["swap 1 1", "print", "swap 0 2", "print"])),
        ("rev_even_odd", fmt([1, 2, 3, 4, 5, 6], ["rev 0 5", "print", "rev 0 4", "print", "rev 2 3", "print", "rev 3 3", "print"])),
        ("rot_multiples", fmt([1, 2, 3, 4, 5], ["rot 5", "print", "rot 6", "print", "rot 1000000000", "print", "rot 4", "print"])),
        ("extreme_values", fmt([1000000000, -1000000000, 0, -1000000000], ["minmax 0 3", "minmax 1 1", "find -1000000000", "find 0", "print"])),
        ("find_first_of_duplicates", fmt([5, 5, 5, 2, 5], ["find 5", "rev 0 4", "find 5", "find 2"])),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 6), "medium": rng.randint(1, 200)}.get(size, 1000)
    q = {"small": 8, "medium": 3000}.get(size, 20000)
    lim = {"small": 5}.get(size, 10 ** 9)
    arr = [rng.randint(-lim, lim) for _ in range(n)]
    return fmt(arr, rand_ops(rng, n, q, arr))
