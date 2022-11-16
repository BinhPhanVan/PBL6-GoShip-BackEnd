def validNumber(phone_number):
    if len(phone_number) != 12:
        return False
    for i in range(12):
        if i in [3,7]:
            if phone_number[i] != '-':
                return False
        elif not phone_number[i].isalnum():
            return False
    return True