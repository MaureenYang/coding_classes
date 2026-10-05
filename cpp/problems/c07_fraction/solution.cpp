#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
using namespace std;
typedef long long ll;

class Fraction {
    ll num_, den_;
public:
    Fraction(ll n = 0, ll d = 1) : num_(n), den_(d) {
        if (d == 0) throw domain_error("undefined");
        if (den_ < 0) { num_ = -num_; den_ = -den_; }
        ll g = gcd(num_, den_);            // num_ = 0 時 g = den_，結果是 0/1
        num_ /= g;
        den_ /= g;
    }
    ll num() const { return num_; }
    ll den() const { return den_; }

    Fraction operator+(const Fraction& o) const { return Fraction(num_ * o.den_ + o.num_ * den_, den_ * o.den_); }
    Fraction operator-(const Fraction& o) const { return Fraction(num_ * o.den_ - o.num_ * den_, den_ * o.den_); }
    Fraction operator*(const Fraction& o) const {
        // 先交叉約分，避免溢位
        ll g1 = gcd(num_, o.den_), g2 = gcd(o.num_, den_);
        return Fraction((num_ / g1) * (o.num_ / g2), (den_ / g2) * (o.den_ / g1));
    }
    Fraction operator/(const Fraction& o) const {
        if (o.num_ == 0) throw domain_error("undefined");
        return *this * Fraction(o.den_, o.num_);
    }
    bool operator<(const Fraction& o) const { return num_ * o.den_ < o.num_ * den_; }
    bool operator==(const Fraction& o) const { return num_ == o.num_ && den_ == o.den_; }
};

ostream& operator<<(ostream& os, const Fraction& f) {
    os << f.num();
    if (f.den() != 1) os << '/' << f.den();
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
        if (op == "<") { cout << (x < y ? "true" : "false") << '\n'; continue; }
        if (op == "==") { cout << (x == y ? "true" : "false") << '\n'; continue; }
        try {
            Fraction r = op == "+" ? x + y : op == "-" ? x - y : op == "*" ? x * y : x / y;
            cout << r << '\n';
        } catch (const domain_error& e) {
            cout << e.what() << '\n';
        }
    }
    return 0;
}
