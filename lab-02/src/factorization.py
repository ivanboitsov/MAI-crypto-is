import csv
from gmpy2 import mpz, gcd

CSV_PATH = "variants.csv"
TARGET_VARIANT = 152


def load_variants(path):
    variants = {}
    
    with open(path, newline="") as f:
        reader = csv.reader(f)

        for row in reader:
            if not row or len(row) < 2:
                continue

            variant_raw, b_raw = row[0].strip(), row[1].strip()
            if not variant_raw.isdigit() or not b_raw.isdigit():
                continue
            variants[int(variant_raw)] = mpz(b_raw)

    return variants


def find_common_factor(target_variant, variants):
    if target_variant not in variants:
        raise ValueError(f"Вариант {target_variant} не найден в файле")

    b_target = variants[target_variant]
    results = []

    for i, b_i in variants.items():
        if i == target_variant:
            continue

        g = gcd(b_target, b_i)
        if g != 1 and g != b_target:
            p = g
            q = b_target // p
            results.append((i, p, q))

    return results


if __name__ == "__main__":
    variants = load_variants(CSV_PATH)
    print(f"Загружено вариантов: {len(variants)}")

    matches = find_common_factor(TARGET_VARIANT, variants)

    if not matches:
        print("Общих множителей не найдено.")
    else:
        for i, p, q in matches:
            print(f"Совпадение с вариантом {i}:")
            print(f"  p = {p}")
            print(f"  q = {q}")
            print(f"  проверка p*q == b_{TARGET_VARIANT}: {p * q == variants[TARGET_VARIANT]}")
            print()