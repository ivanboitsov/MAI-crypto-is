import re
import random
import string

KING_JAMES_PATH = "king_james.txt" # - TEXT_1 (King James Bible, Genesis 1) - king_james.txt
DHAMMAPADA_PATH = "dhammapada.txt" # - TEXT_2 (Dhammapada, Chapter I) - dhammapada.txt
WORDS_PATH = "english_words.txt" # - словарь для "случайных слов" - english-words.txt

ALPHABET = string.ascii_lowercase


def load_king_james(path, length=5000):
    """
    Genesis 1 - вырезает текст после '1:1 In the beginning', убирает номера глав/стихов вида '1:1 ', нормализует пробелы.
    """
    raw = open(path, encoding="utf-8").read()
    idx = raw.find("1:1 In the beginning")
    chunk = raw[idx:idx + length * 2]

    clean = chunk.replace("\r\n", "\n")
    clean = re.sub(r"\d+:\d+\s*", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    return clean[:length]


def load_dhammapada(path, length=5000):
    """
    Chapter I (The Twin-Verses) - убирает заголовок главы и номера строф, нормализует пробелы.
    """
    raw = open(path, encoding="utf-8").read()
    idx = raw.find("Chapter I.")
    chunk = raw[idx:idx + length * 2]

    clean = chunk.replace("\r\n", "\n")
    clean = re.sub(r"Chapter [IVXL]+\..*?\n", "", clean)
    clean = re.sub(r"\n\d+\.\s*", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    return clean[:length]


def load_word_list(path):
    words = open(path, encoding="utf-8").read().splitlines()
    return [w for w in words if w.isalpha() and w.islower()]


def compare_texts(text_a, text_b):
    length = min(len(text_a), len(text_b))
    a = text_a[:length].lower()
    b = text_b[:length].lower()

    matches = sum(1 for ca, cb in zip(a, b) if ca == cb)

    ratio = matches / length if length > 0 else 0.0
    return matches, length, ratio


def random_letters_text(length, alphabet=ALPHABET, seed=None):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(length))


def random_words_text(length, word_list, seed=None):
    rng = random.Random(seed)
    chars = []

    while len(chars) < length:
        word = rng.choice(word_list)
        chars.extend(word)
        chars.append(" ")

    return "".join(chars)[:length]


def prepare_texts(text_a, text_b):
    length = min(len(text_a), len(text_b))
    return text_a[:length], text_b[:length]


def run_scenarios(text_1, text_2, word_list, length, verbose=True):
    results = {}

    t1 = text_1[:length]
    t2 = text_2[:length]

    a, b = prepare_texts(t1, t2)
    results["1. Осмысленный + осмысленный"] = compare_texts(a, b)

    a = t1
    b = random_letters_text(length)
    results["2. Осмысленный + случайные буквы"] = compare_texts(a, b)

    a = t1
    b = random_words_text(length, word_list)
    results["3. Осмысленный + случайные слова"] = compare_texts(a, b)

    a = random_letters_text(length)
    b = random_letters_text(length)
    results["4. Случайные буквы + случайные буквы"] = compare_texts(a, b)

    a = random_words_text(length, word_list)
    b = random_words_text(length, word_list)
    results["5. Случайные слова + случайные слова"] = compare_texts(a, b)

    if verbose:
        for name, (matches, total, ratio) in results.items():
            print(f"  {name}: {matches}/{total} = {ratio:.4f}")

    return results


if __name__ == "__main__":
    MAIN_LENGTH = 5000

    text_1 = load_king_james(KING_JAMES_PATH, MAIN_LENGTH)
    text_2 = load_dhammapada(DHAMMAPADA_PATH, MAIN_LENGTH)
    word_list = load_word_list(WORDS_PATH)

    print(f"TEXT_1 (King James, Genesis 1), {len(text_1)} символов:")
    print(text_1[:300] + " ...\n")

    print(f"TEXT_2 (Dhammapada, Chapter I), {len(text_2)} символов:")
    print(text_2[:300] + " ...\n")

    # Основной прогон на полной длине
    print(f"=== Основной прогон, длина = {MAIN_LENGTH} символов ===")
    run_scenarios(text_1, text_2, word_list, MAIN_LENGTH)
    print()

    # Демонстрация сходимости при разных длинах
    print("=== Сходимость результата при увеличении длины текста ===")
    for length in (50, 200, 1000, 5000):
        print(f"\n-- длина = {length} --")
        run_scenarios(text_1, text_2, word_list, length)
