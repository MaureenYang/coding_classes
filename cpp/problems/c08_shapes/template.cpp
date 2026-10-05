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

// TODO: class Circle : public Shape { ... };
// TODO: class Rectangle : public Shape { ... };
// TODO: class Square : public Rectangle { ... };
// TODO: class Triangle : public Shape { ... };

int main() {
    int n;
    cin >> n;
    vector<unique_ptr<Shape>> shapes;
    for (int i = 0; i < n; i++) {
        string kind;
        cin >> kind;
        // TODO: 依 kind 建立對應的物件，例如 shapes.push_back(make_unique<Circle>(r));
    }

    // TODO: 依面積排序並輸出

    return 0;
}
