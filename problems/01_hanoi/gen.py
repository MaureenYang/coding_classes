TITLE = "河內塔"
TOPIC = "遞迴"
DIFFICULTY = "★☆☆"
TIME_LIMIT = 2.0
RANDOM_PLAN = [("small", 4), ("medium", 2)]


def manual_cases():
    return [
        ("n1_single_disk", "1"),
        ("n2_sample", "2"),
        ("n3", "3"),
        ("n18_max", "18"),
    ]


def random_case(rng, size):
    n = {"small": rng.randint(1, 6), "medium": rng.randint(7, 15)}.get(size, rng.randint(16, 18))
    return f"{n}"
