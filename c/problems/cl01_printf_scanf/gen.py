TITLE = "格式化輸入輸出"
TOPIC = "printf/scanf"
DIFFICULTY = "★☆☆"
TIME_LIMIT = 1.0

PRINTABLE = "".join(chr(c) for c in range(33, 127))


def fmt(lines):
    return f"{len(lines)}\n" + "\n".join(lines)


def rand_float(rng, big):
    v = rng.uniform(-big, big)
    return f"{v:.{rng.randint(0, 6)}f}"


def rand_line(rng, big):
    k = rng.randrange(5)
    if k == 0:
        return f"int {rng.randint(-big, big)}"
    if k == 1:
        return f"float {rand_float(rng, min(big, 10 ** 6))}"
    if k == 2:
        n = rng.randint(1, 20)
        return "str " + "".join(rng.choice(PRINTABLE) for _ in range(n))
    if k == 3:
        return "char " + rng.choice(PRINTABLE)
    return f"time {rng.randint(0, big)} {rng.randint(0, big)} {rng.randint(0, big)}"


def manual_cases():
    return [
        ("sample", fmt(["int 42", "int -255", "float 3.14159", "str hello", "time 1 59 75"])),
        ("int_edges", fmt(["int 0", "int -1", "int 1000000000", "int -1000000000", "int 99999", "int 123456", "int -7"])),
        ("float_rounding", fmt(["float 2.675", "float 0.005", "float -0.04", "float 0", "float 1000000", "float -999999.999999",
                                "float 0.000001", "float 12345.6789", "float 100", "float 0.0001234"])),
        ("str_lengths", fmt(["str a", "str ab", "str abc", "str abcdefghij", "str abcdefghijk", "str 12345678901234567890", "str %d%s%%"])),
        ("chars", fmt(["char a", "char z", "char A", "char 0", "char ~", "char %", "char !"])),
        ("time_carry", fmt(["time 0 0 0", "time 0 0 59", "time 0 0 60", "time 0 59 60", "time 23 59 59", "time 99 0 0",
                            "time 0 0 3600", "time 1000000 1000000 1000000"])),
        ("mixed_whitespace", "3\n  int   5\nchar\n  q\nstr\tx\n"),
    ]


def random_case(rng, size):
    t = {"small": 5, "medium": 200}.get(size, 1000)
    big = {"small": 100}.get(size, 10 ** 9)
    lines = []
    for _ in range(t):
        line = rand_line(rng, big)
        if line.startswith("time"):
            parts = line.split()
            line = "time " + " ".join(str(min(int(x), 10 ** 6)) for x in parts[1:])
        lines.append(line)
    return fmt(lines)
