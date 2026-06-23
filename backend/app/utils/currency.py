def format_inr(amount: float) -> str:
    """Format amount as Indian Rupees with Indian digit grouping."""
    sign = "-" if amount < 0 else ""
    value = abs(float(amount))
    integer_part, decimal_part = f"{value:.2f}".split(".")
    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups + [last_three])
    return f"{sign}₹{formatted_int}.{decimal_part}"
