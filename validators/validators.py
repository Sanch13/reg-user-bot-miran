import re


def validate_full_name(full_name):
    # Регулярное выражение для проверки только русских или английских букв
    pattern = r'^[a-zA-Zа-яА-ЯёЁ\s]+$'
    if not re.match(pattern, full_name):
        raise ValueError("Неверный формат ФИО")
