#include <iostream>
using namespace std;
typedef long long ll;

void kth_move(int n, ll k, char from, char via, char to) {
    while (true) {
        ll half = 1LL << (n - 1);  // 中間那一步是第 half 步
        if (k == half) {
            cout << "disk " << n << ": " << from << " -> " << to << '\n';
            return;
        }
        if (k < half) {
            // 前半段：hanoi(n-1, from, to, via)
            swap(via, to);
        } else {
            // 後半段：hanoi(n-1, via, from, to)
            k -= half;
            swap(from, via);
        }
        n--;
    }
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
