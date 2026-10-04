#include <iostream>
#include <vector>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<long long> a(n);
    for (auto& x : a) cin >> x;

    vector<long long> ans(n, -1);
    vector<int> st;  // 存索引，對應的值由底到頂遞減（非嚴格）
    for (int i = 0; i < n; i++) {
        while (!st.empty() && a[st.back()] < a[i]) {
            ans[st.back()] = a[i];
            st.pop_back();
        }
        st.push_back(i);
    }
    for (int i = 0; i < n; i++) cout << ans[i] << (i + 1 < n ? ' ' : '\n');
    return 0;
}
