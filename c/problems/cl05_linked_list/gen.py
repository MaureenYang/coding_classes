TITLE = "C 語言的鏈結串列"
TOPIC = "struct/指標"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def rand_ops(rng, q, max_slow, val, print_limit):
    ops, vals, slow = [], [], 0
    for _ in range(q):
        r = rng.random()
        x = rng.randint(-val, val)
        if r < 0.25:
            ops.append(f"pushf {x}"); vals.insert(0, x)
        elif r < 0.5:
            ops.append(f"pushb {x}"); vals.append(x)
        elif r < 0.62:
            ops.append("popf")
            if vals: vals.pop(0)
        elif r < 0.72 and slow < max_slow:
            t = rng.choice(vals) if vals and rng.random() < 0.7 else x
            ops.append(f"del {t}"); slow += 1
            if t in vals: vals.remove(t)
        elif r < 0.77 and slow < max_slow:
            ops.append("rev"); vals.reverse(); slow += 1
        elif r < 0.8 and slow < max_slow:
            ops.append("uniq"); slow += 1
            vals = [v for k, v in enumerate(vals) if k == 0 or vals[k - 1] != v]
        elif r < 0.9:
            ops.append(rng.choice(["size", "ends"]))
        elif len(vals) <= print_limit:
            ops.append("print")
        else:
            ops.append("ends")
    return ops


def manual_cases():
    return [
        ("sample", fmt(["pushb 2", "pushb 3", "pushf 1", "pushb 3", "print", "del 3", "ends", "rev", "pushb 0", "print"])),
        ("empty_list_ops", fmt(["popf", "del 1", "rev", "uniq", "size", "ends", "print"])),
        ("single_node", fmt(["pushb 5", "ends", "rev", "ends", "uniq", "del 5", "ends", "size", "pushf 6", "ends", "pushb 7", "ends"])),
        ("del_tail_then_pushb", fmt(["pushb 1", "pushb 2", "pushb 3", "del 3", "ends", "pushb 4", "print", "ends"])),
        ("del_head_and_missing", fmt(["pushb 1", "pushb 2", "del 1", "ends", "del 1", "del 2", "ends", "size", "pushb 9", "ends"])),
        ("pop_to_empty_then_pushb", fmt(["pushf 1", "popf", "ends", "pushb 2", "ends", "popf", "pushf 3", "ends"])),
        ("rev_then_push_both_ends", fmt(["pushb 1", "pushb 2", "pushb 3", "rev", "ends", "pushb 0", "pushf 4", "print", "ends"])),
        ("uniq_cases", fmt(["pushb 1", "pushb 1", "pushb 2", "pushb 1", "pushb 1", "uniq", "print", "ends", "size",
                            "pushb 7", "pushb 7", "pushb 7", "uniq", "print", "ends"])),
        ("uniq_all_same", fmt(["pushb 4"] * 6 + ["uniq", "print", "ends", "size", "pushb 5", "ends"])),
        ("del_first_of_duplicates", fmt(["pushb 2", "pushb 1", "pushb 2", "del 2", "print", "ends"])),
        ("many_nodes_freed", fmt([f"pushb {i}" for i in range(100000)] + [f"pushf {i}" for i in range(99990)] + ["size", "ends"])),
    ]


def random_case(rng, size):
    q = {"small": 12, "medium": 5000}.get(size, 200000)
    return fmt(rand_ops(rng, q, 2000, {"small": 3}.get(size, 10 ** 9), {"small": 100}.get(size, 30)))
