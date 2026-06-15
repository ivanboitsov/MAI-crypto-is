import time
import random

INFINITY = None


def mod_inverse(k, p):
    return pow(k, p - 2, p)


def is_quadratic_residue(a, p):
    if a % p == 0:
        return True
    return pow(a, (p - 1) // 2, p) == 1


def sqrt_mod(a, p):
    assert p % 4 == 3, "sqrt_mod реализован только для p % 4 == 3"
    return pow(a, (p + 1) // 4, p)


class EllipticCurve:
    """
    Кривая y^2 = x^3 + a*x + b (mod p).
    """

    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p

        disc = (4 * a**3 + 27 * b**2) % p
        if disc == 0:
            raise ValueError("Кривая вырожденная: 4a^3 + 27b^2 = 0 (mod p)")

    def is_on_curve(self, point):
        if point is INFINITY:
            return True
        x, y = point
        return (y * y - (x**3 + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        """
        Сложение двух точек на кривой (с учётом удвоения и точки O).
        """
        p = self.p

        if P is INFINITY:
            return Q
        if Q is INFINITY:
            return P

        x1, y1 = P
        x2, y2 = Q

        if x1 == x2 and (y1 + y2) % p == 0:
            return INFINITY

        if P == Q:
            num = (3 * x1 * x1 + self.a) % p
            den = (2 * y1) % p
        else:
            num = (y2 - y1) % p
            den = (x2 - x1) % p

        lam = (num * mod_inverse(den, p)) % p

        x3 = (lam * lam - x1 - x2) % p
        y3 = (lam * (x1 - x3) - y1) % p

        return (x3, y3)

    def scalar_mult(self, k, P):
        result = INFINITY
        addend = P

        while k:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1

        return result


def find_point(curve, max_attempts=10000):
    p = curve.p

    for _ in range(max_attempts):
        x = random.randint(0, p - 1)
        rhs = (x**3 + curve.a * x + curve.b) % p

        if is_quadratic_residue(rhs, p):
            y = sqrt_mod(rhs, p)
            point = (x, y)
            assert curve.is_on_curve(point)
            return point

    raise RuntimeError("Не удалось найти точку на кривой за заданное число попыток")


def brute_force_order(curve, G, log_every=None):
    """
    Вычисляет порядок точки G полным перебором: G, 2G, 3G, ... до O.
    Возвращает (n, elapsed_seconds).
    """
    start = time.perf_counter()

    current = G
    n = 1

    while current is not INFINITY:
        current = curve.add(current, G)
        n += 1

        if log_every and n % log_every == 0:
            elapsed = time.perf_counter() - start
            print(f"    ... n={n}, прошло {elapsed:.2f} сек")

    elapsed = time.perf_counter() - start
    return n, elapsed


def find_prime(bits, rng=None):
    rng = rng or random

    while True:
        candidate = rng.getrandbits(bits) | 1
        candidate |= (1 << (bits - 1))
        if candidate % 4 != 3:
            continue
        if is_prime(candidate):
            return candidate


def is_prime(n, k=20):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n == p:
            return True
        if n % p == 0:
            return False

    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


if __name__ == "__main__":
    BITS = 30

    print(f"Подбираем простое p размером {BITS} бит (p % 4 == 3)...")
    p = find_prime(BITS)
    print(f"p = {p}")

    while True:
        a = random.randint(0, p - 1)
        b = random.randint(0, p - 1)
        try:
            curve = EllipticCurve(a, b, p)
            break
        except ValueError:
            continue

    print(f"Кривая: y^2 = x^3 + {a}x + {b} (mod {p})")

    G = find_point(curve)
    print(f"Точка G = {G}")
    print(f"G на кривой: {curve.is_on_curve(G)}")

    # Полный перебор порядка
    print("\nЗапускаем полный перебор порядка точки...")
    n, elapsed = brute_force_order(curve, G, log_every=1_000_000)

    print(f"\nПорядок точки G: n = {n}")
    print(f"Время выполнения: {elapsed:.2f} сек ({elapsed/60:.2f} мин)")

    # Проверка: n*G должно быть O
    check = curve.scalar_mult(n, G)
    print(f"Проверка n*G == O: {check is INFINITY}")
