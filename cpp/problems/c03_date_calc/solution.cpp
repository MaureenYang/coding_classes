#include <cstdio>
#include <iostream>
#include <string>
using namespace std;
typedef long long ll;

bool is_leap(ll y) { return (y % 4 == 0 && y % 100 != 0) || y % 400 == 0; }

int days_in_month(ll y, ll m) {
    switch (m) {
        case 2: return is_leap(y) ? 29 : 28;
        case 4: case 6: case 9: case 11: return 30;   // 刻意的 fall-through
        default: return 31;
    }
}

bool valid(ll y, ll m, ll d) {
    return 1 <= y && y <= 9999 && 1 <= m && m <= 12 && 1 <= d && d <= days_in_month(y, m);
}

ll to_days(ll y, ll m, ll d) {
    ll py = y - 1;
    ll n = py * 365 + py / 4 - py / 100 + py / 400;   // 前面整年的天數
    for (ll i = 1; i < m; i++) n += days_in_month(y, i);
    return n + d - 1;
}

void from_days(ll n, ll& y, ll& m, ll& d) {
    y = n / 366 + 1;                                  // 先猜一個不會太大的年份，再往後調
    while (to_days(y + 1, 1, 1) <= n) y++;
    n -= to_days(y, 1, 1);
    m = 1;
    while (n >= days_in_month(y, m)) n -= days_in_month(y, m++);
    d = n + 1;
}

int main() {
    const char* names[7] = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"};
    const ll LAST = to_days(9999, 12, 31);
    int Q;
    cin >> Q;
    while (Q--) {
        string op;
        cin >> op;
        if (op == "leap") {
            ll y; cin >> y;
            puts(is_leap(y) ? "yes" : "no");
        } else if (op == "valid") {
            ll y, m, d; cin >> y >> m >> d;
            puts(valid(y, m, d) ? "yes" : "no");
        } else if (op == "weekday") {
            ll y, m, d; cin >> y >> m >> d;
            if (!valid(y, m, d)) puts("invalid");
            else puts(names[to_days(y, m, d) % 7]);
        } else if (op == "diff") {
            ll y1, m1, d1, y2, m2, d2;
            cin >> y1 >> m1 >> d1 >> y2 >> m2 >> d2;
            if (!valid(y1, m1, d1) || !valid(y2, m2, d2)) puts("invalid");
            else printf("%lld\n", to_days(y2, m2, d2) - to_days(y1, m1, d1));
        } else if (op == "add") {
            ll y, m, d, k; cin >> y >> m >> d >> k;
            if (!valid(y, m, d)) { puts("invalid"); continue; }
            ll n = to_days(y, m, d) + k;
            if (n < 0 || n > LAST) { puts("invalid"); continue; }
            from_days(n, y, m, d);
            printf("%04lld-%02lld-%02lld\n", y, m, d);
        }
    }
    return 0;
}
