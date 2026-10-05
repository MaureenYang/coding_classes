#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
using namespace std;
typedef long long ll;

class Fraction {
    ll num_, den_;   // 不變量：最簡、den_ > 0
public:
    Fraction(ll n = 0, ll d = 1) : num_(n), den_(d) {
        // TODO: 分母 0 → throw domain_error；標準化
    }
    ll num() const { return num_; }
    ll den() const { return den_; }

    // TODO: operator+ - * / < ==
};

ostream& operator<<(ostream& os, const Fraction& f) {
    // TODO
    return os;
}

Fraction parse(const string& s) {
    size_t slash = s.find('/');
    if (slash == string::npos) return Fraction(stoll(s));
    return Fraction(stoll(s.substr(0, slash)), stoll(s.substr(slash + 1)));
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int T;
    cin >> T;
    while (T--) {
        string a, op, b;
        cin >> a >> op >> b;
        Fraction x = parse(a), y = parse(b);
        // TODO
    }
    return 0;
}
