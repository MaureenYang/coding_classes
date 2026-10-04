TITLE = "二元搜尋樹"
TOPIC = "BST"
DIFFICULTY = "★★★"
TIME_LIMIT = 2.0


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def ins(xs):
    return [f"insert {x}" for x in xs]


def manual_cases():
    return [
        ("sample", fmt(ins([5, 3, 8, 7, 9]) + ["preorder", "delete 5", "preorder", "inorder", "height"])),
        ("empty_tree", fmt(["inorder", "preorder", "height", "find 1", "delete 1"])),
        ("duplicate_insert", fmt(ins([2, 2, 1, 2, 3, 1]) + ["inorder", "height"])),
        ("delete_leaf", fmt(ins([5, 3, 8]) + ["delete 3", "preorder", "delete 8", "preorder", "height"])),
        ("delete_one_child", fmt(ins([5, 3, 2, 8, 9]) + ["delete 3", "preorder", "delete 8", "preorder"])),
        ("delete_root_repeatedly", fmt(ins([50, 30, 70, 20, 40, 60, 80, 65]) + ["delete 50", "preorder"] * 9 + ["height"])),
        ("successor_has_right_child", fmt(ins([10, 5, 20, 15, 17, 30]) + ["delete 10", "preorder", "inorder"])),
        ("delete_twice", fmt(ins([1, 2]) + ["delete 1", "delete 1", "preorder"])),
        ("negative_and_extreme", fmt(ins([0, -1000000000, 1000000000, -1, 1]) + ["inorder", "preorder", "find -1000000000", "find 999999999"])),
        ("skewed_increasing_2000", fmt(ins(range(2000)) + ["height", "find 1999", "delete 0", "height", "preorder"])),
        ("skewed_decreasing_2000", fmt(ins(range(2000, 0, -1)) + ["height", "delete 2000", "height", "inorder"])),
    ]


def random_case(rng, size):
    q = {"small": rng.randint(1, 15), "medium": 500}.get(size, 5000)
    v = {"small": 9, "medium": 200}.get(size, 10 ** 9)
    pool = [rng.randint(-v, v) for _ in range(max(3, q // 3))]
    ops = []
    for _ in range(q):
        r = rng.random()
        x = rng.choice(pool)
        if r < 0.45:
            ops.append(f"insert {x}")
        elif r < 0.65:
            ops.append(f"delete {x}")
        elif r < 0.8:
            ops.append(f"find {x}")
        elif r < (0.9 if size != "large" else 0.81):
            ops.append(rng.choice(["inorder", "preorder"]))
        else:
            ops.append("height")
    return fmt(ops)
