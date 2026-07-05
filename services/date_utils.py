from datetime import date, timedelta


def today_key():
    return date.today().isoformat()


def today_label():
    return date.today().strftime("%d/%m/%Y")


def previous_day_key(value):
    try:
        return (date.fromisoformat(str(value)) - timedelta(days=1)).isoformat()
    except ValueError:
        return None


def format_date(value):
    if not value:
        return "-"
    parts = str(value).split("-")
    if len(parts) != 3:
        return str(value)
    return f"{parts[2]}/{parts[1]}/{parts[0]}"


def format_day_count(value):
    days = to_int(value)
    if days == 1:
        return "1 dia"
    return f"{days} dias"


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
