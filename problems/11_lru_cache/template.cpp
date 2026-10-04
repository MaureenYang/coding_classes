#include <iostream>
#include <list>
#include <string>
#include <unordered_map>
using namespace std;

class LRUCache {
    int cap;
    list<pair<int, int>> items;  // (key, value)，前面 = 最近使用
    unordered_map<int, list<pair<int, int>>::iterator> pos;

public:
    LRUCache(int c) : cap(c) {}

    // 找到回傳 true 並把值放進 out
    bool get(int k, int& out) {
        // TODO
        return false;
    }

    // 若有淘汰，回傳 true 並把被淘汰的 key 放進 evicted
    bool put(int k, int v, int& evicted) {
        // TODO
        return false;
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int C, Q;
    cin >> C >> Q;
    LRUCache cache(C);
    while (Q--) {
        string op;
        cin >> op;
        if (op == "get") {
            int k, v;
            cin >> k;
            cout << (cache.get(k, v) ? v : -1) << '\n';
        } else {
            int k, v, ev;
            cin >> k >> v;
            if (cache.put(k, v, ev)) cout << "evict " << ev << '\n';
        }
    }
    return 0;
}
