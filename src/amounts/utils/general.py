#!/usr/bin/env python3

import dataclasses, enum

def print_error(message: str):
	"""
	Print an error message.
	"""
	print(f"ERROR: {message}")

class __QuoteType(enum.Enum):
	"""
	Enum containing supported quote types.
	"""
	NONE     = "none"
	SINGLE   = "single"
	DOUBLE   = "double"
	BACKTICK = "backtick"

class Quote(enum.Enum):
	"""
	Enum containing quotes.
	"""
	NONE     = ""
	SINGLE   = "\x27"
	DOUBLE   = "\x22"
	BACKTICK = "\x60"

	@classmethod
	def types(cls):
		"""
		Get all supported quote types.
		"""
		return [__QuoteType.NONE, __QuoteType.SINGLE, __QuoteType.DOUBLE, __QuoteType.BACKTICK]

	@classmethod
	def all(cls):
		"""
		Get all quotes.
		"""
		return [cls.NONE, cls.SINGLE, cls.DOUBLE, cls.BACKTICK]

	@classmethod
	def get(cls, type: str):
		"""
		Get a quote for the specified quote type.
		"""
		mapping = {
			__QuoteType.NONE    : cls.NONE,
			__QuoteType.SINGLE  : cls.SINGLE,
			__QuoteType.DOUBLE  : cls.DOUBLE,
			__QuoteType.BACKTICK: cls.BACKTICK
		}
		return mapping[__QuoteType(type)]

class Separator(enum.Enum):
	"""
	Enum containing separators.
	"""
	SPACE = "\x20"
	COMMA = "\x2C"
	DOT   = "\x2E"
	AND   = "\x26"

class Currency(enum.Enum):
	"""
	Enum containing fiat currency symbols.
	"""
	USD = "\x24"
	EUR = "\u20AC"
	GBP = "\xA3"

@dataclasses.dataclass
class BracketDetails:
	"""
	Class for storing bracket details.
	"""
	left : str
	right: str

class Bracket(enum.Enum):
	"""
	Enum containing brackets.
	"""
	PARENTHESIS = BracketDetails("\x28", "\x29")
	SQUARE      = BracketDetails("\x5B", "\x5D")
	CURLY       = BracketDetails("\x7B", "\x7D")
	ANGLE       = BracketDetails("\x3C", "\x3E")
