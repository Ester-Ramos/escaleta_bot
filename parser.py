class TokenNotFound(ValueError):
    ...


class Parser:
    def __init__(self, tokens):
        self.date = None
        self.tokens = tokens
        self.current_token = 0
        self.sections = {}
        self.parse()

    def expect(self, expected):
        the_token = self.tokens[self.current_token]
        if the_token != expected:
            raise TokenNotFound(
                f"Unexpected token: {repr(the_token)} at position {self.current_token}"
            )
        self.current_token += 1
        return the_token

    def advance_newline(self):
        while self.peek() in {" ", "\n"}:
            self.current_token += 1

    def advance_whitespace(self):
        while self.peek() == " ":
            self.current_token += 1

    def peek(self):
        return self.tokens[self.current_token]

    def consume(self):
        next_token = self.tokens[self.current_token]
        self.current_token += 1
        return next_token

    def expect_tokens(self, tokens):
        result = []
        for token in tokens:
            result.append(self.expect(token))
        return result

    def parse_header(self):
        self.advance_whitespace()
        self.expect_tokens("```asciidoc")
        self.advance_newline()

    def consume_until(self, token):
        tokens = []
        while self.peek() != token:
            tokens.append(self.consume())
        return "".join(tokens)

    def parse_date(self):
        self.advance_whitespace()
        self.expect("[")
        date = self.consume_until("]")
        self.expect("]")
        self.advance_newline()
        return date

    def parse_section(self):
        self.advance_whitespace()

        # Parse section header
        try:
            self.expect("=")
        except TokenNotFound:
            return None
        section = self.consume_until("=").strip()
        self.expect("=")

        self.advance_newline()

        items = []
        while True:
            new_item = self.parse_item()
            if not new_item:
                break
            items.append(new_item)
        return (section, items)

    def parse_item(self):
        try:
            self.expect("-")
        except TokenNotFound:
            return None
        self.advance_whitespace()
        item = self.consume_until("\n")
        self.advance_newline()
        return item

    def parse_footer(self):
        self.advance_whitespace()
        self.expect_tokens("```")

    def parse(self):
        self.parse_header()
        self.date = self.parse_date()
        while True:
            section = self.parse_section()
            if not section:
                break
            section_name, items = section
            self.sections[section_name] = items
        self.parse_footer()

