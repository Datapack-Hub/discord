import random
import re

class Uwuifier:
    def __init__(self, spaces_modifier=None, words_modifier=None, exclamations_modifier=None):
        self.faces = [
            "(・`ω´・)",
            ";;w;;",
            "OwO",
            "UwU",
            ">w<",
            "^w^",
            "ÚwÚ",
            "^-^",
            ":3",
            "x3"
        ]
        self.exclamations = ["!?", "?!!", "?!?1", "!!11", "?!?!"]
        self.actions = [
            "*blushes*",
            "*whispers to self*",
            "*cries*",
            "*screams*",
            "*sweats*",
            "*twerks*",
            "*runs away*",
            "*screeches*",
            "*walks away*",
            "*looks at you*",
            "*starts twerking*",
            "*huggles tightly*",
            "*boops your nose*"
        ]
        self.uwu_map = [
            (re.compile(r"(?:r|l)"), "w"),
            (re.compile(r"(?:R|L)"), "W"),
            (re.compile(r"n([aeiou])"), "ny\\1"),
            (re.compile(r"N([aeiou])"), "Ny\\1"),
            (re.compile(r"N([AEIOU])"), "Ny\\1"),
            (re.compile(r"ove"), "uv")
        ]
        self.spaces_modifier = spaces_modifier if spaces_modifier is not None else {"faces": 0.05, "actions": 0.075, "stutters": 0.1}
        self.words_modifier = words_modifier if words_modifier is not None else 1
        self.exclamations_modifier = exclamations_modifier if exclamations_modifier is not None else 1

    def uwuify_words(self, sentence):
        words = sentence.split(" ")
        uwuified_sentence = []

        for word in words:
            if word.isupper() or word.islower():
                seed = random.random()
                for old_word, new_word in self.uwu_map:
                    if seed > self.words_modifier:
                        continue
                    word = re.sub(old_word, new_word, word)
            uwuified_sentence.append(word)
        return " ".join(uwuified_sentence)

    def uwuify_spaces(self, sentence):
        words = sentence.split(" ")
        uwuified_sentence = []
        face_threshold = self.spaces_modifier["faces"]
        action_threshold = self.spaces_modifier["actions"] + face_threshold
        stutter_threshold = self.spaces_modifier["stutters"] + action_threshold

        for index, word in enumerate(words):
            seed = random.random()
            first_character = word[0]

            if seed <= face_threshold:
                if self.faces:
                    word += " " + random.choice(self.faces)
                    self._check_capital(first_character, word, index, words)
            elif seed <= action_threshold:
                if self.actions:
                    word += " " + random.choice(self.actions)
                    self._check_capital(first_character, word, index, words)
            elif seed <= stutter_threshold and not self._is_uri(word):
                stutter_length = random.randint(0, 2)
                word = (first_character + "-") * stutter_length + word

            uwuified_sentence.append(word)
        return " ".join(uwuified_sentence)

    def uwuify_exclamations(self, sentence):
        words = sentence.split(" ")
        pattern = re.compile(r"[?!]+$")
        uwuified_sentence = []

        for word in words:
            if not pattern.search(word) or random.random() > self.exclamations_modifier:
                uwuified_sentence.append(word)
                continue

            word = pattern.sub("", word)
            word += random.choice(self.exclamations)
            uwuified_sentence.append(word)
        return " ".join(uwuified_sentence)

    def uwuify_sentence(self, sentence):
        uwuified_string = sentence
        uwuified_string = self.uwuify_words(uwuified_string)
        uwuified_string = self.uwuify_exclamations(uwuified_string)
        uwuified_string = self.uwuify_spaces(uwuified_string)
        return uwuified_string

    def _check_capital(self, first_character, word, index, words):
        if not first_character.isupper():
            return

        if sum(1 for char in word if char.isupper()) / len(word) > 0.5:
            return

        if index == 0:
            word = first_character.lower() + word[1:]
        else:
            previous_word = words[index - 1]
            if not any(previous_word.endswith(char) for char in ".!?-"):
                return
            word = first_character.lower() + word[1:]

    def _is_uri(self, word):
        return re.match(r"^https?://.*", word) is not None
