#include <algorithm>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

struct Student {
    string name;
    long long score;
    int age;
    int id;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<Student> v(n);
    for (int i = 0; i < n; i++) {
        cin >> v[i].name >> v[i].score >> v[i].age;
        v[i].id = i;
    }
    sort(v.begin(), v.end(), [](const Student& a, const Student& b) {
        if (a.score != b.score) return a.score > b.score;
        if (a.age != b.age) return a.age < b.age;
        if (a.name != b.name) return a.name < b.name;
        return a.id < b.id;
    });
    for (auto& s : v) cout << s.name << ' ' << s.score << ' ' << s.age << '\n';

    // 名字 → (第一次出現的輸入編號, 名次)
    unordered_map<string, pair<int, int>> first;
    for (int r = 0; r < n; r++) {
        auto it = first.find(v[r].name);
        if (it == first.end() || v[r].id < it->second.first) first[v[r].name] = {v[r].id, r + 1};
    }
    int q;
    cin >> q;
    while (q--) {
        string op, name;
        cin >> op >> name;
        auto it = first.find(name);
        cout << (it == first.end() ? -1 : it->second.second) << '\n';
    }
    return 0;
}
