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

    size_t index(ll key) const {
        // TODO: 好的雜湊函數，回傳 0 ~ buckets.size()-1
        return 0;
    }

public:
    HashTable(int nbuckets = 1 << 18) : buckets(nbuckets) {}

    void put(ll k, ll v) { /* TODO */ }
    bool get(ll k, ll& out) const { /* TODO */ return false; }
    bool erase(ll k) { /* TODO */ return false; }
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
