"""JSON Parser Implementation from Scratch

This module demonstrates how to build a JSON parser without using
the built-in json library. It includes:
- Tokenizer (Lexical Analysis)
- Grammar definition using recursive descent parsing
- Error handling with detailed error messages
- Support for all JSON data types
"""

from enum import Enum
from dataclasses import dataclass
from typing import Any, List, Dict, Union, Optional


class TokenType(Enum):
    # Literals
    STRING = "STRING"
    NUMBER = "NUMBER"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NULL = "NULL"
    
    # Structural
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    COLON = "COLON"  # :
    COMMA = "COMMA"  # ,
    
    # Special
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int


class JSONLexer:
    """Tokenizer for converting JSON string into tokens."""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, msg: str):
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {msg}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        return self.text[pos] if pos < len(self.text) else None
    
    def advance(self) -> Optional[str]:
        if self.pos < len(self.text):
            char = self.text[self.pos]
            self.pos += 1
            if char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return char
        return None
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.text):
            char = self.peek()
            
            if char in ' \t\n\r':
                self.advance()
                continue
            
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, '{', self.line, self.column))
                self.advance()
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, '}', self.line, self.column))
                self.advance()
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, '[', self.line, self.column))
                self.advance()
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, ']', self.line, self.column))
                self.advance()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', self.line, self.column))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', self.line, self.column))
                self.advance()
            elif char == '"':
                self.tokenize_string()
            elif char == '-' or char.isdigit():
                self.tokenize_number()
            elif char == 't' or char == 'f' or char == 'n':
                self.tokenize_keyword()
            else:
                self.error(f"Unexpected character: {char}")
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
    
    def tokenize_string(self):
        start_line, start_col = self.line, self.column
        self.advance()  # skip opening quote
        result = ""
        
        while self.peek() != '"':
            char = self.peek()
            if char is None:
                self.error("Unterminated string")
            elif char == '\\':
                self.advance()
                escaped = self.advance()
                if escaped == '"': result += '"'
                elif escaped == '\\': result += '\\'
                elif escaped == '/': result += '/'
                elif escaped == 'b': result += '\b'
                elif escaped == 'f': result += '\f'
                elif escaped == 'n': result += '\n'
                elif escaped == 'r': result += '\r'
                elif escaped == 't': result += '\t'
                elif escaped == 'u':
                    hex_digits = ""
                    for _ in range(4):
                        hex_digits += self.advance()
                    result += chr(int(hex_digits, 16))
                else:
                    self.error(f"Invalid escape sequence: \\{escaped}")
            else:
                result += char
                self.advance()
        
        self.advance()  # skip closing quote
        self.tokens.append(Token(TokenType.STRING, result, start_line, start_col))
    
    def tokenize_number(self):
        start_line, start_col = self.line, self.column
        result = ""
        
        # Optional minus
        if self.peek() == '-':
            result += self.advance()
        
        # Integer part
        if self.peek() == '0':
            result += self.advance()
        else:
            while self.peek() and self.peek().isdigit():
                result += self.advance()
        
        # Decimal part
        if self.peek() == '.':
            result += self.advance()
            while self.peek() and self.peek().isdigit():
                result += self.advance()
        
        # Exponent part
        if self.peek() in 'eE':
            result += self.advance()
            if self.peek() in '+-':
                result += self.advance()
            while self.peek() and self.peek().isdigit():
                result += self.advance()
        
        try:
            value = float(result) if '.' in result or 'e' in result or 'E' in result else int(result)
        except ValueError:
            self.error(f"Invalid number: {result}")
        
        self.tokens.append(Token(TokenType.NUMBER, value, start_line, start_col))
    
    def tokenize_keyword(self):
        start_line, start_col = self.line, self.column
        result = ""
        
        while self.peek() and self.peek().isalpha():
            result += self.advance()
        
        if result == "true":
            self.tokens.append(Token(TokenType.TRUE, True, start_line, start_col))
        elif result == "false":
            self.tokens.append(Token(TokenType.FALSE, False, start_line, start_col))
        elif result == "null":
            self.tokens.append(Token(TokenType.NULL, None, start_line, start_col))
        else:
            self.error(f"Invalid keyword: {result}")


class JSONParser:
    """Parser using recursive descent parsing."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def error(self, msg: str):
        token = self.current_token()
        raise SyntaxError(f"Parse error at line {token.line}, column {token.column}: {msg}")
    
    def current_token(self) -> Token:
        return self.tokens[min(self.pos, len(self.tokens) - 1)]
    
    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        return self.tokens[min(pos, len(self.tokens) - 1)]
    
    def advance(self) -> Token:
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            self.error(f"Expected {token_type.value}, got {token.type.value}")
        return self.advance()
    
    def parse(self) -> Any:
        """Parse JSON value"""
        result = self.parse_value()
        if self.current_token().type != TokenType.EOF:
            self.error("Expected end of input")
        return result
    
    def parse_value(self) -> Any:
        token = self.current_token()
        
        if token.type == TokenType.STRING:
            self.advance()
            return token.value
        elif token.type == TokenType.NUMBER:
            self.advance()
            return token.value
        elif token.type == TokenType.TRUE:
            self.advance()
            return True
        elif token.type == TokenType.FALSE:
            self.advance()
            return False
        elif token.type == TokenType.NULL:
            self.advance()
            return None
        elif token.type == TokenType.LBRACE:
            return self.parse_object()
        elif token.type == TokenType.LBRACKET:
            return self.parse_array()
        else:
            self.error(f"Unexpected token: {token.type.value}")
    
    def parse_object(self) -> Dict[str, Any]:
        self.expect(TokenType.LBRACE)
        obj = {}
        
        # Empty object
        if self.current_token().type == TokenType.RBRACE:
            self.advance()
            return obj
        
        while True:
            # Key must be string
            key_token = self.expect(TokenType.STRING)
            key = key_token.value
            
            self.expect(TokenType.COLON)
            value = self.parse_value()
            
            obj[key] = value
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
                # Check for trailing comma
                if self.current_token().type == TokenType.RBRACE:
                    self.error("Trailing comma in object")
            else:
                break
        
        self.expect(TokenType.RBRACE)
        return obj
    
    def parse_array(self) -> List[Any]:
        self.expect(TokenType.LBRACKET)
        arr = []
        
        # Empty array
        if self.current_token().type == TokenType.RBRACKET:
            self.advance()
            return arr
        
        while True:
            arr.append(self.parse_value())
            
            if self.current_token().type == TokenType.COMMA:
                self.advance()
                # Check for trailing comma
                if self.current_token().type == TokenType.RBRACKET:
                    self.error("Trailing comma in array")
            else:
                break
        
        self.expect(TokenType.RBRACKET)
        return arr


def parse_json(json_string: str) -> Any:
    """Main entry point for parsing JSON."""
    lexer = JSONLexer(json_string)
    tokens = lexer.tokenize()
    parser = JSONParser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # Example usage
    test_cases = [
        '{"name": "Alice", "age": 30}',
        '[1, 2, 3, {"key": "value"}]',
        '{"nested": {"object": true}, "array": [false, null]}',
    ]
    
    for test in test_cases:
        print(f"Input: {test}")
        result = parse_json(test)
        print(f"Output: {result}")
        print()
