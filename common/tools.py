def atoi(s, default=0):
    result = default
    try:
        result = int(s)
    except ValueError:
        pass
    return result
