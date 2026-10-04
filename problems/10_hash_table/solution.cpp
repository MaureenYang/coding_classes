#include <iostream>
#include <string>
#include <vector>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;

class HashTable {
    struct Entry { ll key, val; };
    vector<vector<Entry>> buckets;
    int n = 0;

    // splitmix64：把 key 的每個位元都充分打亂，再取低位元
    static ull mix(ull x) {
        x += 0x9e3779b97f4a7c15ULL;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
        x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
        return x ^ (x >> 31);
    }
    size_t index(ll key) const { return mix((ull)key) & (buckets.size() - 1); }

public:
    HashTable(int nbuckets = 1 << 18) : buckets(nbuckets) {}

    void put(ll k, ll v) {
        auto& b = buckets[index(k)];
        for (auto& e : b) if (e.key == k) { e.val = v; return; }
        b.push_back({k, v});
        n++;
    }
    bool get(ll k, ll& out) const {
        for (auto& e : buckets[index(k)]) if (e.key == k) { out = e.val; return true; }
        return false;
    }
    bool erase(ll k) {
        auto& b = buckets[index(k)];
        for (size_t i = 0; i < b.size(); i++) {
            if (b[i].key == k) {
                b[i] = b.back();  // 和最後一個交換再刪掉，O(1)
                b.pop_back();
                n--;
                return true;
            }
        }
        return false;
    }
    int size() const { return n; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int Q;
    cin >> Q;
    HashTable h;
    while (Q--) {
        string op;
        cin >> op;
        ll k, v;
        if (op == "put") { cin >> k >> v; h.put(k, v); }
        else if (op == "get") {
            cin >> k;
            if (h.get(k, v)) cout << v << '\n'; else cout << "not found\n";
        } else if (op == "erase") {
            cin >> k;
            cout << (h.erase(k) ? "ok" : "not found") << '\n';
        } else if (op == "size") cout << h.size() << '\n';
    }
    return 0;
}
