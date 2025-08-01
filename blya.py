# перетворюємо неправильною розкладкою текст у читаємий текст
# Як це працює:
# 1. Використовується функція str.maketrans, щоб створити таблицю відповідності символів.
# 2. translate застосовує цю таблицю для заміни символів в рядку.
# 3. Ви можете розширити таблицю, додавши додаткові символи або обробку для інших мовних пар
import pyperclip

def fix_keyboard_layout():
    # Карта відповідності символів
    eng_to_ukr = str.maketrans(
        "qwertyuiop[]asdfghjkl;'zxcvbnm,.QWERTYUIOP}{ASDFGHJKL:\"ZXCVBNM<>&йцукенгшщзхїфівапролджєячсмитьбю?ЙЦУКЕНГШЩЗЇХФІВАПРОЛДЖЄЯЧСМИТЬБЮ",
        "йцукенгшщзхїфівапролджєячсмитьбюЙЦУКЕНГШЩЗЇХФІВАПРОЛДЖЄЯЧСМИТЬБЮ?qwertyuiop[]asdfghjkl;'zxcvbnm,.&QWERTYUIOP}{ASDFGHJKL:\"ZXCVBNM<>"
    )
    wrong_text = pyperclip.paste()
    correct_text = wrong_text.translate(eng_to_ukr)
    pyperclip.copy(correct_text)
    print('Translated:\n', correct_text, '<<<', wrong_text)

