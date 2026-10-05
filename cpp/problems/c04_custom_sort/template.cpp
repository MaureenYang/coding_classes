#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

struct Student {
    string name;
    long long score;
    int age;
    int id;  // 輸入順序
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

    // TODO: 用 lambda 排序

    for (auto& s : v) cout << s.name << ' ' << s.score << ' ' << s.age << '\n';

    int q;
    cin >> q;
    // TODO: 處理 rank 查詢（想想看怎麼避免每次都掃一遍）
    return 0;
}
