#include <iostream>
#include <list>
#include <string>
#include <unordered_map>
using namespace std;

class LRUCache {
    int cap;
    list<pair<int, int>> items;
    unordered_map<int, list<pair<int, int>>::iterator> pos;

public:
    LRUCache(int c) : cap(c) { pos.reserve(2 * c + 16); }

    bool get(int k, int& out) {
        auto it = pos.find(k);
        if (it == pos.end()) return false;
        items.splice(items.begin(), items, it->second);  // 移到最前面，iterator 仍有效
        out = it->second->second;
        return true;
    }

    bool put(int k, int v, int& evicted) {
        auto it = pos.find(k);
        if (it != pos.end()) {
            it->second->second = v;
            items.splice(items.begin(), items, it->second);
            return false;
        }
        bool ev = false;
        if ((int)items.size() == cap) {
            evicted = items.back().first;
            pos.erase(evicted);
            items.pop_back();
            ev = true;
        }
        items.emplace_front(k, v);
        pos[k] = items.begin();
        return ev;
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
