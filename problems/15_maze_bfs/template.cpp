#include <iostream>
#include <queue>
#include <string>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int R, C;
    cin >> R >> C;
    vector<string> g(R);
    for (auto& row : g) cin >> row;

    const int dr[4] = {-1, 1, 0, 0};
    const int dc[4] = {0, 0, -1, 1};
    vector<vector<int>> dist(R, vector<int>(C, -1));
    queue<pair<int, int>> q;

    // TODO: 找到 S，放進 queue；BFS；輸出 T 的距離

    return 0;
}
