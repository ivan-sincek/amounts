#!/usr/bin/env python3

from . import general

import decimal, enum, re, struct

class Category(enum.Enum):
	"""
	Enum containing numeric categories.
	"""
	MINIMUM = "minimum"
	MIDDLE  = "middle"
	MAXIMUM = "maximum"

class Type(enum.Enum):
	"""
	Enum containing numeric types.
	"""
	INTEGER = "integer"
	DECIMAL = "decimal"

class Scope(enum.Enum):
	"""
	Enum containing numeric scopes.
	"""
	MINUS = "\x2D"
	PLUS  = "\x2B"
	NONE  = ""

# ----------------------------------------

class Amount:

	def __init__(self, value: str, category: Category, type: Type):
		"""
		Class for storing amount details.
		"""
		self.category          = category
		self.type              = type
		self.numeric           = decimal.Decimal(value)
		self.string            = str(self.numeric)
		self.scope             = self.__get_scope()
		self.string_no_scope   = self.__get_string_no_scope()
		self.decimal_precision = self.__get_decimal_precision()
		self.bin               = self.__get_bin()
		self.hex               = self.__get_hex()
		self.hex_no_fp         = self.__get_hex_no_fp()
		self.byte              = self.__get_byte()
		self.unicode           = self.__get_unicode()
		self.overflow          = self.__get_overflow()
		self.underflow         = self.__get_underflow()

	def __get_scope(self):
		"""
		Returns 'Scope.MINUS' if the amount is negative, or 'Scope.NONE' if the amount is positive.
		"""
		return Scope.MINUS if self.string.startswith(Scope.MINUS.value) else Scope.NONE

	def __get_string_no_scope(self):
		"""
		Returns the amount without its scope.
		"""
		return self.string.lstrip(self.scope.value)

	def __get_decimal_precision(self):
		"""
		Returns the decimal precision of the amount.
		"""
		return len(self.string.split(general.Separator.DOT.value, 1)[-1]) if type == Type.DECIMAL else 0

	def __get_bin(self):
		"""
		Convert the amount to its binary representation.
		"""
		if self.type == Type.INTEGER:
			return bin(int(self.numeric))
		elif self.type == Type.DECIMAL:
			return "0b" + format(struct.unpack("!I", struct.pack("!f", self.numeric))[0], "032b")

	def __get_hex(self):
		"""
		Convert the amount to its hexadecimal representation.
		"""
		if self.type == Type.INTEGER:
			return hex(int(self.string))
		elif self.type == Type.DECIMAL:
			return float(self.string).hex()

	def __get_hex_no_fp(self):
		"""
		Remove the floating pointer from the hexadecimal representation of the amount.
		"""
		if self.type == Type.INTEGER:
			return self.hex
		elif self.type == Type.DECIMAL:
			base, decimal = self.hex.split(general.Separator.DOT.value)
			decimal = re.search("\d+", decimal)
			return base + decimal.group(0) if decimal else self.hex

	def __get_byte(self):
		"""
		Convert the amount to a byte escape sequence.
		"""
		return ("").join(f"\\x{ord(char):02x}" for char in self.string)

	def __get_unicode(self):
		"""
		Convert the amount to a Unicode escape sequence.
		"""
		return ("").join(f"\\u{ord(char):04x}" for char in self.string)

	def __get_overflow(self, number: int = 1):
		"""
		Increment the amount by the specified number.
		"""
		return str(self.numeric + number)

	def __get_underflow(self, number: int = 1):
		"""
		Decrement the amount by the specified number.
		"""
		return str(self.numeric - number)

# ----------------------------------------

def is_integer(value: str):
	"""
	Check if a value is of type integer.
	"""
	return bool(re.match(r"^[\x2D]{0,1}\d+$", value))

def is_decimal(value: str):
	"""
	Check if a value is of type decimal.
	"""
	return bool(re.match(r"^[\x2D]{0,1}\d+[\x2E]{0,1}\d+$", value))

def __validate(value: str, category: Category) -> tuple[Amount | None, str]:
	"""
	Validate a value.\n
	Returns 'None' and an error message on failure.
	"""
	tmp = None
	message = ""
	if is_integer(value):
		tmp = Amount(value, category, Type.INTEGER)
	elif is_decimal(value):
		tmp = Amount(value, category, Type.DECIMAL)
	else:
		message = f"{category.value.capitalize()} amount must be either an integer or a decimal"
	return tmp, message

def validate_minimum(value: str):
	"""
	Validate a value.\n
	Returns 'None' and an error message on failure.
	"""
	return __validate(value, Category.MINIMUM)

def validate_middle(value: str):
	"""
	Validate a value.\n
	Returns 'None' and an error message on failure.
	"""
	return __validate(value, Category.MIDDLE)

def validate_maximum(value: str):
	"""
	Validate a value.\n
	Returns 'None' and an error message on failure.
	"""
	return __validate(value, Category.MAXIMUM)
