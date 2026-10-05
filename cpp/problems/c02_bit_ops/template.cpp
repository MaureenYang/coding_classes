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
            // TODO
        } else if (op == "lowbit") {
            // TODO
        } else if (op == "highbit") {
            // TODO
        } else if (op == "ctz") {
            // TODO
        } else if (op == "ispow2") {
            // TODO
        } else {
            int k;
            cin >> k;
            // TODO: set / clear / toggle / test / rotl
        }
    }
    return 0;
}
