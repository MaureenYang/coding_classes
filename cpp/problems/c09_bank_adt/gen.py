TITLE = "銀行帳戶系統"
TOPIC = "ADT/繼承"
DIFFICULTY = "★★★"
TIME_LIMIT = 1.0

CAP = 10 ** 15


def fmt(ops):
    return f"{len(ops)}\n" + "\n".join(ops)


def simulate(rng, q, nid, amt_max, report_rate):
    ids = [f"a{i}" for i in range(nid)]
    acc = {}  # id -> [type, param, balance]
    ops = []
    while len(ops) < q:
        r = rng.random()
        i, j = rng.choice(ids), rng.choice(ids)
        amt = rng.choice([rng.randint(1, amt_max), rng.randint(1, amt_max), 0, -rng.randint(1, 5)])
        if r < 0.12:
            if rng.random() < 0.5:
                ops.append(f"open savings {i} {rng.randint(0, 20)}")
                acc.setdefault(i, ["savings", None, 0])
                if acc[i][1] is None: acc[i][1] = int(ops[-1].split()[-1])
            else:
                ops.append(f"open checking {i} {rng.randint(0, amt_max)}")
                acc.setdefault(i, ["checking", None, 0])
                if acc[i][1] is None: acc[i][1] = int(ops[-1].split()[-1])
        elif r < 0.35:
            if i in acc and amt > 0 and abs(acc[i][2] + amt) > CAP:
                continue
            ops.append(f"deposit {i} {amt}")
            if i in acc and amt > 0: acc[i][2] += amt
        elif r < 0.55:
            ops.append(f"withdraw {i} {amt}")
            if i in acc and amt > 0:
                t, p, b = acc[i]
                if b - amt >= (0 if t == "savings" else -p): acc[i][2] -= amt
        elif r < 0.8:
            if i in acc and j in acc and amt > 0 and abs(acc[j][2] + amt) > CAP:
                continue
            ops.append(f"transfer {i} {j} {amt}")
            if i in acc and j in acc and amt > 0 and i != j:
                t, p, b = acc[i]
                if b - amt >= (0 if t == "savings" else -p):
                    acc[i][2] -= amt; acc[j][2] += amt
        elif r < 0.86:
            nxt = {k: (v[2] + v[2] * v[1] // 100 if v[0] == "savings" else (v[2] - 10 if v[2] < 0 else v[2]))
                   for k, v in acc.items()}
            if any(abs(x) > CAP for x in nxt.values()):
                continue
            ops.append("month")
            for k in acc: acc[k][2] = nxt[k]
        elif r < 0.86 + report_rate:
            ops.append("report")
        else:
            ops.append(f"balance {i}")
    return ops


def manual_cases():
    return [
        ("sample", fmt(["open savings amy 10", "open checking bob 100", "deposit amy 50", "transfer amy bob 80",
                        "transfer bob amy 90", "withdraw bob 20", "month", "report", "balance cat"])),
        ("empty_bank", fmt(["report", "month", "balance x", "deposit x 5", "transfer x y 1"])),
        ("duplicate_open", fmt(["open savings a 5", "open checking a 100", "report"])),
        ("error_priority", fmt(["open savings a 0", "open savings b 0", "transfer a zz -5", "transfer zz a 0",
                                "transfer a a -1", "transfer a a 5", "transfer a b 5", "deposit zz -1", "withdraw a 0"])),
        ("exact_limits", fmt(["open savings s 0", "open checking c 100", "deposit s 50", "withdraw s 50", "withdraw s 1",
                              "withdraw c 100", "withdraw c 1", "balance c", "month", "balance c", "deposit c 10", "balance c"])),
        ("transfer_atomic", fmt(["open savings a 0", "open savings b 0", "deposit a 10", "transfer a b 11",
                                 "balance a", "balance b", "transfer a b 10", "report"])),
        ("interest_floor", fmt(["open savings a 7", "deposit a 99", "month", "balance a", "month", "balance a",
                                "open savings z 20", "month", "report"])),
        ("checking_fee_below_limit", fmt(["open checking c 0", "month", "balance c", "deposit c 5", "withdraw c 5",
                                          "open checking d 5", "withdraw d 5", "month", "month", "balance d", "withdraw d 1"])),
        ("report_sorted_by_id", fmt(["open savings b 0", "open savings B 0", "open checking a1 0", "open savings a 0",
                                     "open checking 9 0", "report"])),
    ]


def random_case(rng, size):
    q, nid, amt, rep = {"small": (15, 3, 20, 0.05), "medium": (3000, 30, 1000, 0.02)}.get(size, (100000, 200, 10 ** 9, 0.0005))
    return fmt(simulate(rng, q, nid, amt, rep))
