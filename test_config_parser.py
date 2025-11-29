#!/usr/bin/env python3
"""
Тесты для парсера конфигурационного языка - Вариант 9
"""

import unittest
from main import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def test_parse_number(self):
        self.assertEqual(self.parser.parse_number("123"), 123)
        self.assertEqual(self.parser.parse_number("-456"), -456)

    def test_parse_string(self):
        self.assertEqual(self.parser.parse_string('"hello"'), "hello")

    def test_parse_array(self):
        # array обрабатывается как отдельный токен
        tokens = ['array', '(', '1', ',', '2', ',', '3', ')']
        result, index = self.parser.parse_array(tokens, 0)
        self.assertEqual(result, [1, 2, 3])

    def test_constant_declaration(self):
        text = 'global port = 8080'
        result = self.parser.parse(text)
        self.assertEqual(result['port'], 8080)

    def test_constant_expression_addition(self):
        text = 'global x = @[+ 5 3]'
        result = self.parser.parse(text)
        self.assertEqual(result['x'], 8)

    def test_constant_expression_subtraction(self):
        text = 'global y = @[- 10 4]'
        result = self.parser.parse(text)
        self.assertEqual(result['y'], 6)

    def test_constant_expression_multiplication(self):
        text = 'global z = @[* 3 4]'
        result = self.parser.parse(text)
        self.assertEqual(result['z'], 12)

    def test_constant_expression_division(self):
        text = 'global w = @[/ 15 3]'
        result = self.parser.parse(text)
        self.assertEqual(result['w'], 5)

    def test_function_abs(self):
        text = 'global x = abs(-5)'
        result = self.parser.parse(text)
        self.assertEqual(result['x'], 5)

    def test_function_ord(self):
        text = 'global x = ord("A")'
        result = self.parser.parse(text)
        self.assertEqual(result['x'], 65)

    def test_array_with_constants(self):
        text = 'global size = 3\nglobal numbers = array(1, 2, size)'
        result = self.parser.parse(text)
        self.assertEqual(result['numbers'], [1, 2, 3])

    def test_complex_config(self):
        text = '''global port = 8080
global host = "localhost"
global max_conn = @[+ 100 50]
global features = array("auth", "logging")'''
        result = self.parser.parse(text)
        self.assertEqual(result['port'], 8080)
        self.assertEqual(result['host'], "localhost")
        self.assertEqual(result['max_conn'], 150)
        self.assertEqual(result['features'], ["auth", "logging"])

    def test_tokenize(self):
        text = 'global x = @[+ 1 2] // comment'
        tokens = self.parser.tokenize(text)
        self.assertEqual(tokens, ['global', 'x', '=', '@[', '+', '1', '2', ']'])

if __name__ == '__main__':
    unittest.main()