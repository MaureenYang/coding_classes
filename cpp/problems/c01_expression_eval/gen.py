TITLE = "運算式求值"
TOPIC = "運算式"
DIFFICULTY = "★★☆"
TIME_LIMIT = 1.0
RANDOM_PLAN = [("small", 4), ("medium", 3), ("large", 2)]

LIMIT = 10 ** 18
PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}


class DivZero(Exception):
    pass


class Overflow(Exception):
    pass


def cdiv(a, b):
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def ev(node):
    """用 C++ 的語意計算；超出範圍丟 Overflow"""
    kind = node[0]
    if kind == "num":
        v = node[1]
    elif kind == "neg":
        v = -ev(node[1])
    else:
        a, b = ev(node[1]), ev(node[2])
        op = kind
        if op == "+": v = a + b
        elif op == "-": v = a - b
        elif op == "*": v = a * b
        else:
            if b == 0:
                raise DivZero()
            q = cdiv(a, b)
            v = q if op == "/" else a - b * q
    if abs(v) > LIMIT:
        raise Overflow()
    return v


def prec(node):
    return {"num": 4, "neg": 3}.get(node[0], PREC.get(node[0]))


def render(node, rng):
    kind = node[0]
    if kind == "num":
        s = str(node[1])
    elif kind == "neg":
        c = render(node[1], rng)
        if prec(node[1]) < 3:
            c = "(" + c + ")"
        s = "-" + c
    else:
        l, r = render(node[1], rng), render(node[2], rng)
        if prec(node[1]) < PREC[kind]:
            l = "(" + l + ")"
        if prec(node[2]) <= PREC[kind]:
            r = "(" + r + ")"
        sp = lambda: " " * rng.choice([0, 0, 1, 1, 2])
        s = l + sp() + kind + sp() + r
    if rng.random() < 0.08:
        s = "(" + s + ")"
    return s


def build(rng, size, maxv):
    if size <= 1:
        node = ("num", rng.randint(0, maxv))
        return ("neg", node) if rng.random() < 0.2 else node
    if rng.random() < 0.1:
        return ("neg", build(rng, size, maxv))
    left = rng.randint(1, size - 1)
    op = rng.choice("+-*/%+-*")
    return (op, build(rng, left, maxv), build(rng, size - left, maxv))


def gen_expr(rng, size, maxv, allow_div0=True):
    while True:
        node = build(rng, size, maxv)
        try:
            ev(node)
        except Overflow:
            continue
        except DivZero:
            if not allow_div0 or rng.random() < 0.7:
                continue
        return render(node, rng)


def fmt(lines):
    return f"{len(lines)}\n" + "\n".join(lines)


def manual_cases():
    return [
        ("sample", fmt(["1 + 2 * 3", "(1 + 2) * 3", "10 - 4 - 3", "-7 / 2", "-7 % 3", "5 / (3 - 3)"])),
        ("single_number", fmt(["0", "42", "1000000000", "  7  "])),
        ("truncate_toward_zero", fmt(["7 / 2", "-7 / 2", "7 / -2", "-7 / -2", "1 / 3", "-1 / 3"])),
        ("modulo_sign_follows_dividend", fmt(["7 % 3", "-7 % 3", "7 % -3", "-7 % -3", "0 % 5", "6 % 3"])),
        ("left_associative", fmt(["10 - 4 - 3", "100 / 10 / 5", "2 * 3 % 4", "100 % 7 * 3", "1 - 2 + 3 - 4"])),
        ("unary_minus", fmt(["-3", "--3", "---3", "2 - -3", "2--3", "-(2 + 3)", "-2 * -3", "-(-(-1))"])),
        ("precedence", fmt(["2 + 3 * 4 - 5", "2 * 3 + 4 * 5", "1 + 10 % 3", "(1 + 10) % 3", "8 / 2 * 4"])),
        ("division_by_zero_anywhere", fmt(["1 / 0", "1 % 0", "0 * (5 / 0)", "3 + 4 % (2 - 2)", "(1 - 1) / (1 - 1)", "0 / 5"])),
        ("big_numbers", fmt(["1000000000 * 1000000000", "-1000000000 * 1000000000",
                             "1000000000 * 1000000000 / 7", "1000000000 * 1000000000 % 1000000007"])),
        ("deep_parentheses", fmt(["(" * 300 + "1" + ")" * 300, "-" * 200 + "5"])),
    ]


def random_case(rng, size):
    t, sz, maxv = {"small": (5, 4, 9), "medium": (200, 15, 1000)}.get(size, (1000, 120, 10 ** 9))
    return fmt([gen_expr(rng, rng.randint(1, sz), maxv) for _ in range(t)])
