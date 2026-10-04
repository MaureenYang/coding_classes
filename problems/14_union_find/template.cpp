#include <iostream>
#include <string>
#include <vector>
using namespace std;

struct DSU {
    vector<int> parent, sz;
    int groups;
    DSU(int n) : parent(n + 1), sz(n + 1, 1), groups(n) {
        for (int i = 0; i <= n; i++) parent[i] = i;
    }
    int find(int x) {
        // TODO: 路徑壓縮
        return x;
    }
    void unite(int a, int b) {
        // TODO: 按大小合併，記得更新 groups
    }
    bool same(int a, int b) { return find(a) == find(b); }
    int size(int a) { return sz[find(a)]; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q;
    cin >> n >> q;
    DSU d(n);
    while (q--) {
        string op;
        cin >> op;
        int a, b;
        if (op == "union") { cin >> a >> b; d.unite(a, b); }
        else if (op == "same") { cin >> a >> b; cout << (d.same(a, b) ? "YES" : "NO") << '\n'; }
        else if (op == "size") { cin >> a; cout << d.size(a) << '\n'; }
        else if (op == "count") cout << d.groups << '\n';
    }
    return 0;
}
