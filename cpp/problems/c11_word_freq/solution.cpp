#include <algorithm>
#include <cctype>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int K;
    cin >> K;
    unordered_map<string, int> cnt;
    long long total = 0;
    string word;
    char c;
    auto flush = [&]() {
        if (!word.empty()) { cnt[word]++; total++; word.clear(); }
    };
    while (cin.get(c)) {
        unsigned char u = (unsigned char)c;
        if (isalpha(u)) word += (char)tolower(u);
        else flush();
    }
    flush();   // 最後一個單字

    vector<pair<string, int>> v(cnt.begin(), cnt.end());
    sort(v.begin(), v.end(), [](const auto& a, const auto& b) {
        if (a.second != b.second) return a.second > b.second;
        return a.first < b.first;
    });
    cout << "total: " << total << '\n';
    cout << "distinct: " << v.size() << '\n';
    for (int i = 0; i < K && i < (int)v.size(); i++) cout << v[i].first << ' ' << v[i].second << '\n';
    return 0;
}
