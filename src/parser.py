import re
import collections

# Token specification
PARAM = r"(?P<PARAM>[^\[\]\s]+)"
QUOTEDPARAM = r"\"(?P<QUOTEDPARAM>.*?)\""
SINGQUOTEDPARAM = r"'(?P<SINGQUOTEDPARAM>.*?)'"
LPAREN = r"(?P<LPAREN>\[)"
RPAREN = r"(?P<RPAREN>\])"
WS = r"(?P<WS>\s+)"

master_pat = re.compile("|".join([QUOTEDPARAM, SINGQUOTEDPARAM, PARAM, LPAREN,
                                  RPAREN, WS]))

# Tokenizer
Token = collections.namedtuple("Token", ["type","value"])

def generate_tokens(text):
    scanner = master_pat.scanner(text)
    for m in iter(scanner.match, None):
        tok = Token(m.lastgroup, m.group())
        if tok.type != "WS":
            yield tok

# Parser
class Parser:
    """
    Implementation of a recursive descent parser.   Each method
    implements a single grammar rule.  Use the ._accept() method
    to test and accept the current lookahead token.  Use the ._expect()
    method to exactly match and discard the next token on on the input
    (or raise a SyntaxError if it doesn"t match).
    """

    def parse(self,text):
        self.tokens = generate_tokens(text)
        self.tok = None             # Last symbol consumed
        self.nexttok = None         # Next symbol tokenized
        self._advance()             # Load first lookahead token
        return self.param()

    def _advance(self):
        "Advance one token ahead"
        self.tok, self.nexttok = self.nexttok, next(self.tokens, None)

    def _accept(self,toktype):
        "Test and consume the next token if it matches toktype"
        if self.nexttok and self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self,toktype):
        "Consume next token if it matches toktype or raise SyntaxError"
        if not self._accept(toktype):
            raise SyntaxError("Expected " + toktype)

    # Grammar rules follow

    def param(self):
        "interpert parameters"
        params = []
        while True:
            if self._accept("QUOTEDPARAM"):
                params.append(self.tok.value[1:-1])
            elif self._accept("SINGQUOTEDPARAM"):
                params.append(self.tok.value[1:-1])
            elif self._accept("PARAM"):
                params.append(self.tok.value)
            elif self._accept("LPAREN"):
                params.append(self.param())
                self._expect("RPAREN")
            else:
                break
        return params

if __name__ == "__main__":
    p = Parser()
    assert p.parse("2 3") == ["2", "3"]
    assert p.parse("[2 3]") == [["2", "3"]]
    assert p.parse("1 [2 3]") == ["1", ["2", "3"]]
    assert p.parse("[[2 3][4 5]]") == [[["2", "3"], ["4", "5"]]]
    assert p.parse("[[mot01 3][mot02 5]] ct01 999") ==\
        [[["mot01", "3"], ["mot02", "5"]], "ct01", "999"]
    assert p.parse('"2 3"') == ["2 3"]
    assert p.parse("'2 3'") == ["2 3"]
    assert p.parse("ScanFile file.dat") == ["ScanFile", "file.dat"]
    assert p.parse("2 3 ['Hello world!' 'How are you?']") ==\
        ["2", "3", ["Hello world!", "How are you?"]]
    