
def str2bool(value):
    if value.lower() == str(True).lower():
        return True
    elif value.lower() == str(False).lower():
        return False
    else:
        raise ValueError(f"Unable to parse '{value}'")
