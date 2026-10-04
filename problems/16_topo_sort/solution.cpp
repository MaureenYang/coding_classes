#include <functional>
#include <iostream>
#include <queue>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<vector<int>> adj(n + 1);
    vector<int> indeg(n + 1, 0);
    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        adj[a].push_back(b);
        indeg[b]++;
    }

    priority_queue<int, vector<int>, greater<int>> pq;
    for (int v = 1; v <= n; v++) if (indeg[v] == 0) pq.push(v);
    vector<int> order;
    while (!pq.empty()) {
        int u = pq.top();
        pq.pop();
        order.push_back(u);
        for (int v : adj[u]) if (--indeg[v] == 0) pq.push(v);
    }
    if ((int)order.size() < n) {
        cout << "IMPOSSIBLE\n";
    } else {
        for (int i = 0; i < n; i++) cout << order[i] << (i + 1 < n ? ' ' : '\n');
    }
    return 0;
}
