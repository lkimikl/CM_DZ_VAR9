#!/usr/bin/env python3
"""
Инструмент командной строки для преобразования учебного конфигурационного языка в YAML
Вариант №9
"""

import sys
import argparse
import re
import yaml
from typing import Any, Dict, List, Union


class ConfigParser:
    def __init__(self):
        self.constants = {}
        self.operations = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else 0
        }
        self.functions = {
            'ord': lambda x: ord(x) if isinstance(x, str) and len(x) == 1 else 65,
            'abs': abs
        }

    def parse_number(self, token: str) -> Union[int, float]:
        """Парсинг чисел"""
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                raise ValueError(f"Invalid number: {token}")

    def parse_string(self, token: str) -> str:
        """Парсинг строк"""
        if token.startswith('"') and token.endswith('"'):
            return token[1:-1]
        raise ValueError(f"Invalid string: {token}")

    def parse_array(self, tokens: List[str], index: int) -> tuple[List[Any], int]:
        """Парсинг массивов"""
        index += 1  # Пропускаем 'array'

        if index >= len(tokens) or tokens[index] != '(':
            raise ValueError(f"Expected '(' after array, got '{tokens[index]}'")

        index += 1
        values = []

        while index < len(tokens) and tokens[index] != ')':
            if tokens[index] == ',':
                index += 1
                continue
            value, index = self.parse_value(tokens, index)
            values.append(value)

        if index >= len(tokens) or tokens[index] != ')':
            raise ValueError("Expected ')'")
        return values, index + 1

    def parse_constant_expression(self, tokens: List[str], index: int) -> tuple[Any, int]:
        """Парсинг константных выражений"""
        index += 1  # Пропускаем '@['

        if index >= len(tokens):
            raise ValueError("Incomplete expression")

        # Собираем все токены до ]
        parts = []
        while index < len(tokens) and tokens[index] != ']':
            parts.append(tokens[index])
            index += 1

        if index >= len(tokens) or tokens[index] != ']':
            raise ValueError("Expected ']'")

        # Обрабатываем выражение в префиксной форме
        if len(parts) >= 3 and parts[0] in self.operations:
            operator = parts[0]
            arg1 = self._parse_expression_value(parts[1])
            arg2 = self._parse_expression_value(parts[2])
            result = self.operations[operator](arg1, arg2)
            return result, index + 1
        elif len(parts) >= 2 and parts[0] in self.functions:
            func_name = parts[0]
            arg = self._parse_expression_value(parts[1])
            result = self.functions[func_name](arg)
            return result, index + 1
        else:
            raise ValueError(f"Invalid expression: {parts}")

    def _parse_expression_value(self, token: str) -> Any:
        """Парсинг значения внутри выражения"""
        if token in self.constants:
            return self.constants[token]
        elif re.match(r'^-?\d+$', token):
            return int(token)
        elif re.match(r'^-?\d+\.\d+$', token):
            return float(token)
        elif token.startswith('"') and token.endswith('"'):
            return token[1:-1]
        else:
            raise ValueError(f"Unknown value in expression: {token}")

    def parse_function_call(self, tokens: List[str], index: int) -> tuple[Any, int]:
        """Парсинг вызовов функций func(аргумент)"""
        func_name = tokens[index]
        index += 1

        if index >= len(tokens) or tokens[index] != '(':
            raise ValueError(f"Expected '(' after {func_name}")
        index += 1

        arg, index = self.parse_value(tokens, index)

        if index >= len(tokens) or tokens[index] != ')':
            raise ValueError(f"Expected ')'")
        return self.functions[func_name](arg), index + 1

    def parse_value(self, tokens: List[str], index: int) -> tuple[Any, int]:
        """Парсинг любого значения"""
        if index >= len(tokens):
            raise ValueError("Unexpected end")

        token = tokens[index]

        if token == 'array':
            return self.parse_array(tokens, index)
        elif token == '@[':
            return self.parse_constant_expression(tokens, index)
        elif token in ['ord', 'abs']:
            return self.parse_function_call(tokens, index)
        elif token.startswith('"') and token.endswith('"'):
            return self.parse_string(token), index + 1
        elif token in self.constants:
            return self.constants[token], index + 1
        else:
            # Пробуем как число
            try:
                return self.parse_number(token), index + 1
            except ValueError:
                raise ValueError(f"Unknown value: {token}")

    def tokenize(self, text: str) -> List[str]:
        """Токенизация"""
        # Удаляем комментарии
        text = re.sub(r'//.*', '', text)

        tokens = []
        i = 0
        n = len(text)

        while i < n:
            if text[i].isspace():
                i += 1
                continue

            # Обрабатываем @[ как один токен
            if text[i:i + 2] == '@[':
                tokens.append('@[')
                i += 2
                continue

            # Строки
            if text[i] == '"':
                j = i + 1
                while j < n and text[j] != '"':
                    j += 1
                if j < n:
                    tokens.append(text[i:j + 1])
                    i = j + 1
                else:
                    raise ValueError("Unclosed string")

            # Специальные токены
            elif text[i] in '(),;=[]':
                tokens.append(text[i])
                i += 1

            # Идентификаторы и числа
            else:
                j = i
                while j < n and not text[j].isspace() and text[j] not in '(),;=[]"@':
                    j += 1
                token = text[i:j]
                if token:
                    tokens.append(token)
                i = j

        return tokens

    def parse(self, text: str) -> Dict[str, Any]:
        """Основной парсер"""
        tokens = self.tokenize(text)
        result = {}
        i = 0

        while i < len(tokens):
            if tokens[i] == 'global' and i + 3 < len(tokens):
                name = tokens[i + 1]
                if tokens[i + 2] == '=':
                    value, i = self.parse_value(tokens, i + 3)
                    self.constants[name] = value
                    result[name] = value
                else:
                    i += 1
            else:
                i += 1

        return result


def main():
    parser = argparse.ArgumentParser(description='Конвертер учебного конфигурационного языка в YAML')
    parser.add_argument('input_file', help='Путь к входному файлу')
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        config_parser = ConfigParser()
        result = config_parser.parse(content)

        yaml_output = yaml.dump(result, default_flow_style=False, allow_unicode=True)
        print(yaml_output)

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()