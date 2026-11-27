#include <stdio.h>
#include <string.h>

typedef unsigned long long u64;
typedef unsigned __int128 u128;

static u64 p, A, B;

static u64 mulmod(u64 a, u64 b) { return (u64)((u128)a * b % p); }
static u64 addm(u64 a, u64 b) { return (a + b) % p; }           /* p < 2^62，不會溢位 */
static u64 subm(u64 a, u64 b) { return (a + p - b) % p; }

static u64 powmod(u64 a, u64 e) {
    u64 r = 1;
    for (a %= p; e; e >>= 1, a = mulmod(a, a))
        if (e & 1) r = mulmod(r, a);
    return r;
}

static u64 inv(u64 a) { return powmod(a, p - 2); }

typedef struct { int inf; u64 x, y; } Point;      /* inf = 1 表示無窮遠點 O */

static Point add(Point P, Point Q) {
    if (P.inf) return Q;
    if (Q.inf) return P;
    if (P.x == Q.x && addm(P.y, Q.y) == 0) return (Point){1, 0, 0};   /* P + (−P) = O */
    u64 lam;
    if (P.x == Q.x)                                                 /* 倍點：切線斜率 */
        lam = mulmod(addm(mulmod(3, mulmod(P.x, P.x)), A), inv(mulmod(2, P.y)));
    else                                                            /* 割線斜率 */
        lam = mulmod(subm(Q.y, P.y), inv(subm(Q.x, P.x)));
    u64 x3 = subm(subm(mulmod(lam, lam), P.x), Q.x);
    u64 y3 = subm(mulmod(lam, subm(P.x, x3)), P.y);
    return (Point){0, x3, y3};
}

static Point mul(u64 k, Point P) {                  /* 倍加法 */
    Point R = {1, 0, 0};
    for (; k; k >>= 1, P = add(P, P))
        if (k & 1) R = add(R, P);
    return R;
}

static Point read_point(void) {
    char s[32];
    scanf("%31s", s);
    if (s[0] == 'O') return (Point){1, 0, 0};
    Point P = {0, 0, 0};
    sscanf(s, "%llu", &P.x);
    scanf("%llu", &P.y);
    return P;
}

static void print_point(Point P) {
    if (P.inf) puts("O");
    else printf("%llu %llu\n", P.x, P.y);
}

int main(void) {
    int q;
    if (scanf("%llu %llu %llu %d", &p, &A, &B, &q) != 4) return 0;
    while (q--) {
        char op[8];
        scanf("%7s", op);
        if (strcmp(op, "ADD") == 0) {
            Point P = read_point();
            Point Q = read_point();
            print_point(add(P, Q));
        } else {
            u64 k;
            scanf("%llu", &k);
            print_point(mul(k, read_point()));
        }
    }
    return 0;
}
