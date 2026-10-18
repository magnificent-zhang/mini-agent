def fibonacci(n):
    """返回斐波那契数列的前 n 项。"""
    seq = []
    a, b = 0, 1
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq


if __name__ == "__main__":
    result = fibonacci(20)
    print(" ".join(str(x) for x in result))
    print("共", len(result), "项，第 20 项 =", result[-1])
