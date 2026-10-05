#include <iostream>
using namespace std;
typedef long long ll;

class Matrix {
public:
    int rows, cols;
    ll** a;

    Matrix(int r, int c) : rows(r), cols(c) {
        // TODO: 配置 r 列、每列 c 個，初始化為 0
        a = nullptr;
    }
    ~Matrix() {
        // TODO: 釋放
    }
    // 禁止複製，避免兩個物件共用同一塊記憶體（第 06 課會教怎麼正確支援複製）
    Matrix(const Matrix&) = delete;
    Matrix& operator=(const Matrix&) = delete;

    void read() {
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++) cin >> a[i][j];
    }
    void print() const {
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++) cout << a[i][j] << (j + 1 < cols ? ' ' : '\n');
    }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int r1, c1, r2, c2;
    cin >> r1 >> c1;
    Matrix A(r1, c1);
    A.read();
    cin >> r2 >> c2;
    Matrix B(r2, c2);
    B.read();

    // TODO: A+B、A*B、T(A)
    return 0;
}
