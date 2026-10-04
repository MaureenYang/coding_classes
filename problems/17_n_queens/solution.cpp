#include <iostream>
#include <vector>
using namespace std;

int n;
long long total = 0;
vector<int> pos, best;
vector<bool> col, diag1, diag2;

void solve(int r) {
    if (r == n) {
        if (total == 0) best = pos;
        total++;
        return;
    }
    for (int c = 0; c < n; c++) {
        if (col[c] || diag1[r + c] || diag2[r - c + n - 1]) continue;
        col[c] = diag1[r + c] = diag2[r - c + n - 1] = true;
        pos[r] = c;
        solve(r + 1);
        col[c] = diag1[r + c] = diag2[r - c + n - 1] = false;
    }
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
