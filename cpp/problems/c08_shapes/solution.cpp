#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <memory>
#include <string>
#include <vector>
using namespace std;

const double PI = acos(-1.0);

class Shape {
public:
    virtual ~Shape() = default;
    virtual string name() const = 0;
    virtual double area() const = 0;
    virtual double perimeter() const = 0;
};

class Circle : public Shape {
    double r_;
public:
    explicit Circle(double r) : r_(r) {}
    string name() const override { return "circle"; }
    double area() const override { return PI * r_ * r_; }
    double perimeter() const override { return 2 * PI * r_; }
};

class Rectangle : public Shape {
protected:
    double w_, h_;
public:
    Rectangle(double w, double h) : w_(w), h_(h) {}
    string name() const override { return "rectangle"; }
    double area() const override { return w_ * h_; }
    double perimeter() const override { return 2 * (w_ + h_); }
};

class Square : public Rectangle {
public:
    explicit Square(double s) : Rectangle(s, s) {}
    string name() const override { return "square"; }
};

class Triangle : public Shape {
    double a_, b_, c_;
public:
    Triangle(double a, double b, double c) : a_(a), b_(b), c_(c) {}
    string name() const override { return "triangle"; }
    double area() const override {
        double s = (a_ + b_ + c_) / 2;
        return sqrt(s * (s - a_) * (s - b_) * (s - c_));
    }
    double perimeter() const override { return a_ + b_ + c_; }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n;
    cin >> n;
    vector<unique_ptr<Shape>> shapes;
    for (int i = 0; i < n; i++) {
        string kind;
        cin >> kind;
        if (kind == "circle") { double r; cin >> r; shapes.push_back(make_unique<Circle>(r)); }
        else if (kind == "rect") { double w, h; cin >> w >> h; shapes.push_back(make_unique<Rectangle>(w, h)); }
        else if (kind == "square") { double s; cin >> s; shapes.push_back(make_unique<Square>(s)); }
        else { double a, b, c; cin >> a >> b >> c; shapes.push_back(make_unique<Triangle>(a, b, c)); }
    }
    stable_sort(shapes.begin(), shapes.end(), [](const unique_ptr<Shape>& x, const unique_ptr<Shape>& y) {
        return x->area() > y->area() + 1e-9;
    });
    cout << fixed << setprecision(2);
    double total = 0;
    for (const auto& s : shapes) {
        cout << s->name() << ' ' << s->area() << ' ' << s->perimeter() << '\n';
        total += s->area();
    }
    cout << "total area: " << total << '\n';
    return 0;
}
