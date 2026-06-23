import re

from pymorphy3 import MorphAnalyzer

morph = MorphAnalyzer()

STOP_WORDS = {
    "и",
    "в",
    "во",
    "на",
    "с",
    "со",
    "для",
    "по",
    "к",
    "ко",
    "от",
    "до",
    "из",
    "у",
    "о",
    "об",
    "при",
    "над",
    "под",
    "это",
    "то",
    "а",
    "но",
    "что",
    "чтобы",
    "как",
    "или",
}


def normalize_word(word):

    parses = morph.parse(word)

    preferred_pos_groups = [
        {"NOUN"},
        {"ADJF", "ADJS"},
        {"VERB", "INFN"},
        {"PRTF", "PRTS", "GRND"},
    ]

    for pos_group in preferred_pos_groups:

        candidates = [
            parsed_word
            for parsed_word in parses
            if parsed_word.tag.POS in pos_group
        ]

        if candidates:

            return max(
                candidates,
                key=lambda parsed_word: parsed_word.score
            ).normal_form

    return parses[0].normal_form


def preprocess_text(text):

    text = text.lower()

    text = re.sub(
        r"[^а-яёa-z0-9\s]",
        " ",
        text
    )

    words = text.split()

    lemmas = []

    for word in words:

        lemma = normalize_word(word)

        if lemma not in STOP_WORDS:

            lemmas.append(lemma)

    return lemmas
