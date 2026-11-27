#include <stdio.h>
#include <string.h>

typedef long long ll;

static int N;
static ll p, q;

static void read_poly(ll *a) {
    for (int i = 0; i < N; i++) scanf("%lld", &a[i]);
}

static void print_poly(const ll *a) {
    for (int i = 0; i < N; i++) printf("%lld%c", a[i], i + 1 < N ? ' ' : '\n');
}

static ll md(ll x, ll m) { x %= m; return x < 0 ? x + m : x; }

/* c = a ⋆ b mod m（卷積：x^N = 1，第 i 項乘第 j 項加到第 (i + j) mod N 項），結果在 [0, m) */
static void conv(const ll *a, const ll *b, ll *c, ll m) {
    /* TODO：注意 c 可能和 a 或 b 是同一個陣列，先算到暫存陣列 */
}

/* 中心提升：每個係數取模 m 後放到 (−m/2, m/2] */
static void lift(ll *a, ll m) {
    /* TODO */
}

int main(void) {
    static ll x[2048], y[2048], z[2048], w[2048];
    int qn;
    if (scanf("%d %lld %lld %d", &N, &p, &q, &qn) != 4) return 0;
    while (qn--) {
        char op[8];
        scanf("%7s", op);
        if (strcmp(op, "KEY") == 0) {
            read_poly(x); read_poly(y);
            /* TODO：h = Fq ⋆ g mod q */
        } else if (strcmp(op, "ENC") == 0) {
            read_poly(x); read_poly(y); read_poly(z);
            /* TODO：e = p·(h ⋆ r) + m mod q */
        } else {
            read_poly(x); read_poly(y); read_poly(z);
            /* TODO：a = f ⋆ e mod q 中心提升；m = Fp ⋆ a mod p 中心提升 */
        }
    }
    return 0;
}
