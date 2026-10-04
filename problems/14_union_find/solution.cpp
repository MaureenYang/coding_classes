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
        int r = x;
        while (parent[r] != r) r = parent[r];
        while (parent[x] != r) {  // 路徑壓縮（迴圈版，不怕 stack overflow）
            int nx = parent[x];
            parent[x] = r;
            x = nx;
        }
        return r;
    }
    void unite(int a, int b) {
        a = find(a), b = find(b);
        if (a == b) return;
        if (sz[a] < sz[b]) swap(a, b);
        parent[b] = a;
        sz[a] += sz[b];
        groups--;
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
