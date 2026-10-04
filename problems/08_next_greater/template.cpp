#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<long long> a(n);
    for (auto& x : a) cin >> x;

    vector<long long> ans(n, -1);
    // TODO: 用 stack 存索引

    for (int i = 0; i < n; i++) cout << ans[i] << (i + 1 < n ? ' ' : '\n');
    return 0;
}
