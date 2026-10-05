TITLE = "日期計算"
TOPIC = "控制流程"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0


def fmt(qs):
    return f"{len(qs)}\n" + "\n".join(qs)


def rand_date(rng, valid_bias=0.8):
    if rng.random() < valid_bias:
        y = rng.choice([rng.randint(1, 9999), rng.choice([1, 4, 100, 400, 1900, 2000, 2024, 9999])])
        m = rng.randint(1, 12)
        d = rng.randint(1, 31 if m != 2 else 29)
    else:
        y = rng.choice([0, -1, 10000, rng.randint(-10000, 10000)])
        m = rng.choice([0, 13, -1, rng.randint(-20, 20)])
        d = rng.choice([0, 32, -5, rng.randint(-40, 40)])
    return y, m, d


def manual_cases():
    return [
        ("sample", fmt(["leap 1900", "valid 2023 2 29", "weekday 2024 1 1", "diff 2024 1 1 2024 3 1",
                        "add 2024 2 28 2", "add 2024 1 1 -1"])),
        ("leap_rules", fmt([f"leap {y}" for y in [1, 4, 100, 200, 300, 400, 1600, 1700, 1900, 2000, 2023, 2024, 2100, 2400, 0, -4, -100]])),
        ("feb_29", fmt(["valid 2000 2 29", "valid 1900 2 29", "valid 2024 2 29", "valid 2023 2 29",
                        "valid 2024 2 30", "weekday 2000 2 29", "add 2024 2 29 365", "add 2024 2 29 366"])),
        ("month_lengths", fmt([f"valid 2023 {m} {d}" for m in range(1, 13) for d in (28, 29, 30, 31)])),
        ("invalid_fields", fmt(["valid 0 1 1", "valid 10000 1 1", "valid 2023 0 1", "valid 2023 13 1",
                                "valid 2023 1 0", "valid -1 -1 -1", "weekday 2023 4 31", "diff 2023 1 1 2023 2 30",
                                "add 2023 6 31 1"])),
        ("first_day_monday", fmt(["weekday 1 1 1", "weekday 1 1 7", "weekday 1 1 8", "diff 1 1 1 9999 12 31",
                                  "diff 9999 12 31 1 1 1", "weekday 9999 12 31"])),
        ("add_out_of_range", fmt(["add 1 1 1 -1", "add 9999 12 31 1", "add 1 1 1 0", "add 9999 12 31 0",
                                  "add 1 1 1 3652058", "add 1 1 1 3652059", "add 5000 6 15 -4000000"])),
        ("year_boundaries", fmt(["add 1999 12 31 1", "add 2000 1 1 -1", "diff 1999 12 31 2000 1 1",
                                 "add 2023 1 31 1", "add 2023 3 1 -1", "add 2024 3 1 -1", "add 5 3 1 0"])),
    ]


def random_case(rng, size):
    q = {"small": 10, "medium": 3000}.get(size, 100000)
    qs = []
    for _ in range(q):
        op = rng.choice(["valid", "leap", "weekday", "diff", "add", "add", "diff"])
        y, m, d = rand_date(rng)
        if op == "leap":
            qs.append(f"leap {y}")
        elif op in ("valid", "weekday"):
            qs.append(f"{op} {y} {m} {d}")
        elif op == "diff":
            y2, m2, d2 = rand_date(rng)
            qs.append(f"diff {y} {m} {d} {y2} {m2} {d2}")
        else:
            n = rng.choice([rng.randint(-400, 400), rng.randint(-4 * 10 ** 6, 4 * 10 ** 6)])
            qs.append(f"add {y} {m} {d} {n}")
    return fmt(qs)
