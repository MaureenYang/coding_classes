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

/* c = a ⋆ b mod m（卷積：x^N = 1），結果在 [0, m) */
static void conv(const ll *a, const ll *b, ll *c, ll m) {
    static ll tmp[2048];
    for (int k = 0; k < N; k++) tmp[k] = 0;
    for (int i = 0; i < N; i++) {
        ll ai = md(a[i], m);
        if (!ai) continue;
        for (int j = 0; j < N; j++) {
            int k = i + j < N ? i + j : i + j - N;
            tmp[k] = (tmp[k] + ai * md(b[j], m)) % m;
        }
    }
    for (int k = 0; k < N; k++) c[k] = tmp[k];
}

/* 中心提升：[0, m) → (−m/2, m/2] */
static void lift(ll *a, ll m) {
    for (int i = 0; i < N; i++) {
        a[i] = md(a[i], m);
        if (a[i] > m / 2) a[i] -= m;
    }
}

int main(void) {
    static ll x[2048], y[2048], z[2048], w[2048];
    int qn;
    if (scanf("%d %lld %lld %d", &N, &p, &q, &qn) != 4) return 0;
    while (qn--) {
        char op[8];
        scanf("%7s", op);
        if (strcmp(op, "KEY") == 0) {              /* h = Fq ⋆ g mod q */
            read_poly(x); read_poly(y);
            conv(x, y, z, q);
            print_poly(z);
        } else if (strcmp(op, "ENC") == 0) {       /* e = p·(h ⋆ r) + m mod q */
            read_poly(x); read_poly(y); read_poly(z);
            conv(x, y, w, q);
            for (int i = 0; i < N; i++) w[i] = md(p * w[i] + z[i], q);
            print_poly(w);
        } else {                                   /* a = f ⋆ e mod q（中心提升），m = Fp ⋆ a mod p（中心提升） */
            read_poly(x); read_poly(y); read_poly(z);
            conv(x, z, w, q);
            lift(w, q);
            conv(y, w, z, p);
            lift(z, p);
            print_poly(z);
        }
    }
    return 0;
}
