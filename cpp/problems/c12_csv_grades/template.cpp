#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

string trim(const string& s) {
    // TODO
    return s;
}

int main() {
    int n;
    cin >> n;
    // TODO: 處理 cin >> 之後殘留的換行

    long long classSum = 0, classCnt = 0;
    cout << fixed << setprecision(2);
    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);
        // TODO: 切欄位、trim、計算平均
    }
    // TODO: 全班平均
    return 0;
}
