

def spanish_title_case(text):
    # Words to keep in lowercase unless they are the first word
    lowercase_words = ['de', 'a', 'en', 'y', 'o', 'u', 'del', 'la', 'los', 'las', 'el', 'un', 'una', 'unos', 'unas']
    words = text.split()
    new_title = []
    for i, word in enumerate(words):
        if word.lower() in lowercase_words and i != 0:
            new_title.append(word.lower())
        else:
            new_title.append(word.capitalize())
    return ' '.join(new_title)