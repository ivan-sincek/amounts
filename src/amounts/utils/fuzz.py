#!/usr/bin/env python3

from . import digit, general

import decimal

# ----------------------------------------

def __separate(amount: digit.Amount, separator: str, group_by: int):
	"""
	Group and separate digits using the specified separator.
	"""
	reverse = ""
	decimal = ""
	if amount.type == digit.Type.INTEGER:
		reverse = amount.string_no_scope[::-1]
	elif amount.type == digit.Type.DECIMAL:
		reverse, decimal = amount.string_no_scope.split(general.Separator.DOT.value, 1)
		reverse = reverse[::-1]
		decimal = general.Separator.DOT.value + decimal
	tmp = ""
	for i in range(0, len(reverse), group_by):
		if i > 0:
			tmp += separator
		tmp += reverse[i:i+group_by]
	tmp = amount.scope.value + tmp[::-1] + decimal
	return tmp

def separators(middle: digit.Amount) -> set[str]:
	"""
	Test grouping and separating digits using separators.
	"""
	tmp = []
	for separator in [general.Separator.SPACE, general.Separator.COMMA, general.Separator.DOT]:
		separator = separator.value
		tmp.append(__separate(middle, separator, 3))
	return tmp

# ----------------------------------------

def zeros(middle: digit.Amount) -> set[str]:
	"""
	Test adding leading zeros and trailing decimal zeros using separators.
	"""
	zeros = "00"
	tmp = [middle.scope.value + zeros + middle.string_no_scope]
	for separator in [general.Separator.COMMA, general.Separator.DOT]:
		separator = separator.value
		if middle.type == digit.Type.INTEGER:
			tmp.append(middle.string + separator + zeros)
		elif middle.type == digit.Type.DECIMAL:
			replaced = middle.string.replace(general.Separator.DOT.value, separator)
			tmp.extend([replaced, replaced + zeros])
	return tmp

# ----------------------------------------

def scopes(middle: digit.Amount) -> set[str]:
	"""
	Test prepending and appending scopes.
	"""
	tmp = []
	for scope in [digit.Scope.MINUS, digit.Scope.PLUS, digit.Scope.NONE]:
		scope = scope.value
		tmp.extend([scope + middle.string_no_scope, middle.string_no_scope + scope])
	return tmp

# ----------------------------------------

def currencies(middle: digit.Amount) -> set[str]:
	"""
	Test prepending fiat currency symbols with and without scopes.
	"""
	tmp = []
	for currency in [general.Currency.USD, general.Currency.EUR, general.Currency.GBP]:
		currency = currency.value
		for scope in [digit.Scope.MINUS, digit.Scope.PLUS, digit.Scope.NONE]:
			scope = scope.value
			tmp.extend([currency + scope + middle.string_no_scope, scope + currency + middle.string_no_scope])
	return tmp

# ----------------------------------------

def enquote(string: str, quote: str):
	"""
	Enclose a string in quotes and escape the inner quotes.
	"""
	return quote + string.replace(quote, f"\\{quote}") + quote

def brackets(middle: digit.Amount, quote: general.Quote, ignore: bool) -> set[str]:
	"""
	Testing adding brackets and extending the inner elements.
	"""
	tmp = []
	quote = general.Quote.DOUBLE.value if quote == general.Quote.NONE else quote.value
	separator = general.Separator.COMMA.value
	for bracket in [general.Bracket.PARENTHESIS, general.Bracket.SQUARE, general.Bracket.CURLY]:
		bracket = bracket.value
		values = [middle.string, enquote(middle.string, quote), middle.string + separator + middle.underflow, enquote(middle.string, quote) + separator + enquote(middle.underflow, quote)]
		if not ignore:
			values = ["", separator * 2] + values
		for value in values:
			tmp.append(bracket.left + value + bracket.right)
	return tmp

# ----------------------------------------

def flows(minimum: digit.Amount, maximum: digit.Amount, ignore: bool) -> set[str]:
	"""
	Test overflows, underflows, and infinite values.
	"""
	tmp = []
	if minimum:
		tmp.append(minimum.underflow)
	if maximum:
		tmp.append(maximum.overflow)
	if not ignore:
		for scope in [digit.Scope.MINUS, digit.Scope.NONE]:
			scope = scope.value
			for value in ["NaN", "Infinity", "inf"]:
				tmp.append(scope + value)
	return tmp

# ----------------------------------------

def notations(minimum: digit.Amount, maximum: digit.Amount, middle: digit.Amount, ignore: bool) -> set[str]:
	"""
	Test binary and hexadecimal representations, exponential notations, and byte and Unicode escape sequences.
	"""
	tmp = [middle.bin, middle.hex, middle.hex_no_fp, middle.hex.strip(), middle.byte, middle.unicode, f"{middle.string}e0", f"{middle.string}e{digit.Scope.MINUS.value}50", format(middle.numeric*decimal.Decimal(10**-50), '.50f')]
	if minimum:
		if minimum.numeric > 0:
			tmp.append(f"{minimum.string}e\x2D1")
		elif minimum.numeric < 0:
			tmp.append(f"{minimum.string}e1")
	if maximum:
		if maximum.numeric > 0:
			tmp.append(f"{maximum.string}e1")
		elif maximum.numeric < 0:
			tmp.append(f"{maximum.string}e\x2D1")
	if not ignore:
		tmp.extend([f"{general.Separator.AND.value}h00", f"{general.Separator.AND.value}hff"])
	return tmp

# ----------------------------------------

def __spread(amount: digit.Amount, separator: str):
	"""
	Separate each digit using the specified separator.
	"""
	base = ""
	decimal = ""
	if amount.type == digit.Type.INTEGER:
		base = amount.string_no_scope
	elif amount.type == digit.Type.DECIMAL:
		base, decimal = amount.string_no_scope.split(general.Separator.DOT.value, 1)
		decimal = general.Separator.DOT.value + decimal
	tmp = ""
	for i in range(len(base)):
		if i > 0:
			tmp += separator
		tmp += base[i]
	tmp = amount.scope.value + tmp + decimal
	return tmp

def other(middle: digit.Amount, ignore: bool) -> set[str]:
	"""
	Test boolean, empty, integer minimum, integer maximum, and other special values.
	"""
	tmp = [__spread(middle, general.Separator.COMMA.value * 2), f"%20%09{middle.string}", f"{middle.string}%20%00%00"]
	if not ignore:
		tmp.extend(["true", "false", "1", "0", f"{digit.Scope.MINUS.value}1", f"{digit.Scope.PLUS.value}1", f"{digit.Scope.MINUS.value}0", f"{digit.Scope.PLUS.value}0", f"0e{digit.Scope.MINUS.value}1", "0e1"])
		tmp.extend(["null", "None", "nil", "An Array"])
		tmp.extend([f"{digit.Scope.MINUS.value}2147483648", "2147483647", f"{digit.Scope.MINUS.value}2147483649", "2147483648", "4294967295", "4294967296"])
	return tmp

# ----------------------------------------

def __generate(char: str, length: int, iterations: int, prepend: str = "", append: str = ""):
	"""
	Generate a string based on the specified parameters.
	"""
	tmp = []
	for i in range(1, iterations + 1):
		string = char * length * i
		if prepend:
			string = prepend + string[len(prepend):]
		if append:
			string = string[:-len(append)] + append
		tmp.append(string)
	return tmp

def lengths(ignore: bool):
	"""
	Test lengths.
	"""
	tmp = []
	if not ignore:
		for scope in [digit.Scope.NONE, digit.Scope.MINUS]:
			scope = scope.value
			tmp.extend(__generate("9", 128, 3, scope))
	return tmp
