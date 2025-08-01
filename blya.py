# перетворюємо текст в неправильній розкладці у читаємий текст
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

