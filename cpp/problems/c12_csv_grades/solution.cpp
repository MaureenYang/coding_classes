#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
using namespace std;

string trim(const string& s) {
    size_t b = s.find_first_not_of(' ');
    if (b == string::npos) return "";
    size_t e = s.find_last_not_of(' ');
    return s.substr(b, e - b + 1);
}

int main() {
    int n;
    cin >> n;
    string line;
    getline(cin, line);   // 吃掉第一行剩下的換行

    long long classSum = 0, classCnt = 0;
    cout << fixed << setprecision(2);
    for (int i = 0; i < n; i++) {
        getline(cin, line);
        stringstream ss(line);
        string field, name;
        getline(ss, name, ',');
        name = trim(name);
        long long sum = 0, cnt = 0;
        while (getline(ss, field, ',')) {
            field = trim(field);
            if (field.empty()) continue;
            sum += stoll(field);
            cnt++;
        }
        classSum += sum;
        classCnt += cnt;
        cout << name << ": ";
        if (cnt == 0) cout << "no scores\n";
        else cout << (double)sum / cnt << '\n';
    }
    cout << "class average: ";
    if (classCnt == 0) cout << "no scores\n";
    else cout << (double)classSum / classCnt << '\n';
    return 0;
}
