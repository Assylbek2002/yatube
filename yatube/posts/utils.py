from django.http import HttpResponseRedirect


codes_ru = {
    "А": ".-",
    "Б": "-...",
    "В": ".--",
    "Г": "--.",
    "Д": "-..",
    "Е": ".",
    "Ж": "...-",
    "З": "--..",
    "И": "..",
    "Й": ".---",
    "К": "-.-",
    "Л": ".-..",
    "М": "--",
    "Н": "-.",
    "О": "---",
    "П": ".--.",
    "Р": ".-.",
    "С": "...",
    "Т": "-",
    "У": "..-",
    "Ф": "..-.",
    "Х": "....",
    "Ц": "-.-.",
    "Ч": "---.",
    "Ш": "----",
    "Щ": "--.-",
    "Ъ": "--.--",
    "Ы": "-.--",
    "Ь": "-..-",
    "Э": "..-..",
    "Ю": "..--"}


def user_only(func):
    def check_user(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(
                redirect_to="/auth/login",
            )
        func(request, *args, **kwargs)

    return check_user


def convert_morse(text, language):
    if language != "ru":
        raise ValueError("Language is not supported")
    if not isinstance(text, str):
        raise TypeError("Wrong text type")
    result = ""
    for symbol in text.upper():
        if symbol not in codes_ru.keys():
            raise ValueError("invalid character")
        result += codes_ru[symbol]
    return result
