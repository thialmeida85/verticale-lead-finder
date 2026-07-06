import re


def only_digits(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def normalize_cnpj(value: str | None) -> str:
    digits = only_digits(value)
    if len(digits) != 14:
        return digits
    return digits


def is_valid_cnpj(value: str | None) -> bool:
    digits = only_digits(value)
    if len(digits) != 14 or digits == digits[0] * 14:
        return False

    def check_digit(numbers: str) -> str:
        weights = range(len(numbers) + 1, 1, -1)
        total = sum(int(number) * weight for number, weight in zip(numbers, weights))
        rest = total % 11
        return "0" if rest < 2 else str(11 - rest)

    first = check_digit(digits[:12])
    second = check_digit(digits[:12] + first)
    return digits[-2:] == first + second


def normalize_phone(value: str | None) -> str | None:
    digits = only_digits(value)
    if not digits:
        return None
    if len(digits) in {10, 11}:
        return f"55{digits}"
    if len(digits) in {12, 13} and digits.startswith("55"):
        return digits
    return digits


def parse_money(value) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(".", "").replace(",", "."))
    except ValueError:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


def truthy(value) -> bool:
    return bool(value not in (None, "", False))


def score_classification(score: int) -> str:
    if score <= 30:
        return "baixo potencial"
    if score <= 60:
        return "medio potencial"
    if score <= 80:
        return "bom potencial"
    return "alto potencial"
