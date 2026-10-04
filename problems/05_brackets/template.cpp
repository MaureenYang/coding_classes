#include <iostream>
#include <stack>
#include <string>
using namespace std;

bool valid(const string& s) {
    stack<char> st;
    for (char c : s) {
        // TODO
    }
    // TODO
    return false;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    while (T--) {
        string s;
        cin >> s;
        cout << (valid(s) ? "YES" : "NO") << '\n';
    }
    return 0;
}
