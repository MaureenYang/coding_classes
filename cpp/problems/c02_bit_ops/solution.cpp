#include <iostream>
#include <string>
using namespace std;
typedef unsigned long long ull;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int Q;
    cin >> Q;
    while (Q--) {
        string op;
        ull x;
        cin >> op >> x;
        if (op == "popcount") {
            int c = 0;
            for (ull t = x; t; t &= t - 1) c++;          // 每次清掉最低的 1
            cout << c << '\n';
        } else if (op == "lowbit") {
            cout << (x & (~x + 1)) << '\n';
        } else if (op == "highbit") {
            int h = -1;
            for (int i = 0; i < 64; i++) if (x >> i & 1ULL) h = i;
            cout << h << '\n';
        } else if (op == "ctz") {
            int c = 0;
            while (c < 64 && !(x >> c & 1ULL)) c++;
            cout << c << '\n';
        } else if (op == "ispow2") {
            cout << (x != 0 && (x & (x - 1)) == 0 ? "yes" : "no") << '\n';
        } else {
            int k;
            cin >> k;
            ull bit = 1ULL << k;
            if (op == "set") cout << (x | bit) << '\n';
            else if (op == "clear") cout << (x & ~bit) << '\n';
            else if (op == "toggle") cout << (x ^ bit) << '\n';
            else if (op == "test") cout << ((x >> k) & 1ULL) << '\n';
            else if (op == "rotl") {
                ull r = (k == 0) ? x : (x << k) | (x >> (64 - k));   // k = 0 時 x >> 64 是 UB
                cout << r << '\n';
            }
        }
    }
    return 0;
}
