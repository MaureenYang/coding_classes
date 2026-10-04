#include <iostream>
#include <vector>
using namespace std;

int n;
long long total = 0;
vector<int> pos, best;               // pos[r] = 第 r 列的皇后在哪一行
vector<bool> col, diag1, diag2;

void solve(int r) {
    // TODO: r == n 代表放完了
    // TODO: 試每一行 c；可以放就標記、遞迴、取消標記
}

int main() {
    cin >> n;
    pos.assign(n, 0);
    col.assign(n, false);
    diag1.assign(2 * n, false);
    diag2.assign(2 * n, false);
    solve(0);
    cout << total << '\n';
    if (best.empty()) cout << "none\n";
    else for (int i = 0; i < n; i++) cout << best[i] + 1 << (i + 1 < n ? ' ' : '\n');
    return 0;
}
