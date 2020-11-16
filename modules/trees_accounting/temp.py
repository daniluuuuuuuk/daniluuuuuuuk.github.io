def roundingData(i):
    """Привожу диаметры стволов"""
    i = float(i) / 10
    if 0 < i <= 12.9:
        # b = 1
        b = 4
    elif 13.0 <= i <= 31.9:
        # b = 2
        b = 4
    elif 32.0 <= i:
        b = 4
    else:
        b = 1
    i = round(i / b + 10 ** (-9)) * b

    if i <= 6:
        return 0

    return i


print(roundingData(59))
