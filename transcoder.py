class Transcoder:

    to_alto_dictionary = {
        '`': '\025',  # \u0060
        '¯': '\025',  # \u00AF
        '‾': '\025',  # \u203E
        '·': '!',     # \u00B7
        '•': '!',     # \u2022
        '⋕': '!',     # \u22D5
        '⁑': '%',     # \u2051
        '←': '_',     # \u2190
        '↑': '^',     # \u2191
        '⇑': '^',     # \u21D1
        '⇒': '?',     # \u21D2
        '∢': '\026',  # \u2222
        '≠': '\016',  # \u2260
        '≡': '\006',  # \u2261
        '≤': '\001',  # \u2264
        '≥': '\022',  # \u2265
        '⊡': '@',     # \u22A1
        '☞': '#'      # \u261E
    }

    @classmethod
    def to_alto(cls, source):
        result = ''
        for each in source:
            result += cls.to_alto_dictionary.get(each, each)
        return result

