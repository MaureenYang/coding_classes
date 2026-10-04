#include <iostream>
using namespace std;
typedef long long ll;

// 回傳：在 hanoi(n, from, via, to) 的過程中，第 k 步是什麼
void kth_move(int n, ll k, char from, char via, char to) {
    // TODO
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    while (T--) {
        int n;
        ll k;
        cin >> n >> k;
        kth_move(n, k, 'A', 'B', 'C');
    }
    return 0;
}
