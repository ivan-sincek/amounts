#!/usr/bin/env python3

import argparse, os, re, struct, sys

# ----------------------------------------

def unique(sequence):
	seen = set()
	return [x for x in sequence if not (x in seen or seen.add(x))]

def write_array(data, out):
	try:
		with open(out, "w") as stream:
			for line in data:
				stream.write(str(line).strip() + "\n")
		print(("Results have been saved to '{0}'").format(out))
	except FileNotFoundError:
		print(("Cannot save results to '{0}'").format(out))

# ----------------------------------------

def is_int(string):
	return re.match(r"^[\-]{0,1}\d+$", string)

def is_float(string):
	return re.match(r"^[\-]{0,1}\d+[\.]{0,1}\d+$", string)

def parse_digit(string, string_type):
	tmp = {
		"type": string_type,
		"scope": "",
		"orig": {
			"str": None,
			"num": None
		},
		"base": {
			"str": None
		}
	}
	const = "\x2D"
	if string.startswith(const):
		tmp["scope"] = const
	if string_type == "int":
		tmp["orig"]["num"] = int(string)
		tmp["orig"]["str"] = str(tmp["orig"]["num"])
	elif string_type == "float":
		tmp["orig"]["num"] = float(string)
		tmp["orig"]["str"] = ("{0:.12f}").format(tmp["orig"]["num"]).rstrip("0")
	tmp["base"]["str"] = tmp["orig"]["str"].lstrip(const)
	return tmp

# ----------------------------------------

def separate(digit, separator, skip = 3):
	scope = digit["scope"]
	decimal = ""
	if digit["type"] == "int":
		digit = digit["base"]["str"][::-1]
	elif digit["type"] == "float":
		const = "\x2E"
		array = digit["base"]["str"].split(const, 1)
		digit = array[0][::-1]
		decimal = const + array[1]
	tmp = ""
	for i in range(0, len(digit), skip):
		if i > 0:
			tmp += separator
		tmp += digit[i:i+skip]
	tmp = scope + tmp[::-1] + decimal
	return tmp

def separators(digit):
	# test amount separators
	tmp = []
	for separator in ["\x20", "\x2E", "\x2C"]:
		tmp.append(separate(digit, separator))
	return unique(tmp)

def zeros(digit):
	# test prepending zeros and appending decimal zeros
	zeros = "0" * 2
	tmp = [
		digit["scope"] + zeros + digit["base"]["str"]
	]
	for separator in ["\x2E", "\x2C"]:
		if digit["type"] == "int":
			tmp.append(digit["orig"]["str"] + separator + zeros)
		elif digit["type"] == "float":
			tmp.append(digit["orig"]["str"].replace(".", separator))
	return unique(tmp)

def scopes(digit):
	# test prepending and appending scopes
	tmp = []
	for scope in ["", "\x2B", "\x2D"]:
		tmp.extend([scope + digit["base"]["str"], digit["base"]["str"] + scope])
	return unique(tmp)

def currencies(digit):
	# test prepending currency symbols - including scopes
	tmp = []
	# $, £, €
	for currency in ["\x24", "\xA3", "\u20AC"]:
		for scope in ["", "\x2D"]:
			tmp.extend([currency + scope + digit["base"]["str"], scope + currency + digit["base"]["str"]])
	return unique(tmp)

def add_quotes(string, quotes):
	return quotes + string.replace(quotes, "\\" + quotes) + quotes

def brackets(digit, quotes = ""):
	# test embracing amount with brackets and expanding
	tmp = []
	if not quotes:
		quotes = "\x22"
	separator = "\x2C"
	const = "X"
	for placeholder in ["\x28" + const + "\x29", "\x5B" + const + "\x5D", "\x7B" + const + "\x7D"]:
		tmp.extend([
			placeholder.replace(const, ""),
			placeholder.replace(const, separator * 2),
			placeholder.replace(const, digit["orig"]["str"]),
			placeholder.replace(const, digit["orig"]["str"] + separator + increment(digit)),
			placeholder.replace(const, add_quotes(digit["orig"]["str"], quotes)),
			placeholder.replace(const, add_quotes(digit["orig"]["str"], quotes) + separator + add_quotes(increment(digit), quotes))
		])
	return unique(tmp)

def increment(digit, value = 1):
	return str(digit["orig"]["num"] + value)

def decrement(digit, value = 1):
	return str(digit["orig"]["num"] - value)

def flows(minimum, maximum):
	# test underflows and overflows
	tmp = [
		decrement(minimum),
		increment(maximum)
	]
	for value in ["NaN", "Infinity", "inf"]:
		for scope in ["", "\x2D"]:
			tmp.append(scope + value)
	return unique(tmp)

def to_bin(digit):
	if digit["type"] == "int":
		return bin(digit["orig"]["num"])
	elif digit["type"] == "float":
		# binary representation of a float number
		return "0b" + format(struct.unpack("!I", struct.pack("!f", digit["orig"]["num"]))[0], "032b") # v1
		# return "0b" + ("").join([("{0:0>8b}").format(char) for char in struct.pack("!f", digit)]) # v2

def to_hex(digit):
	if digit["type"] == "int":
		return hex(digit["orig"]["num"])
	elif digit["type"] == "float":
		return float.hex(digit["orig"]["num"])

def to_ascii_hex(digit):
	const = "\\x"
	return const + const.join([char.encode().hex() for char in digit["orig"]["str"]])

def to_unicode_hex(digit):
	const = "\\u"
	tmp = ""
	for char in digit["orig"]["str"]:
		char = char.encode().hex()
		length = len(char)
		if length > 4:
			continue
		tmp += const + (4 - length) * "0" + char
	return tmp

def notations(minimum, maximum, middle):
	# test binary, hexadecimal, and exponential notations
	tmp = [
		to_bin(middle),
		to_hex(middle),
		to_ascii_hex(middle),
		to_unicode_hex(middle),
		"\x26h00", "\x26hff",
		"0\x2E00000000000000000000000000000000000000000000000001", "1e\x2D50",
		middle["orig"]["str"] + "e0"
	]
	if minimum["orig"]["num"] > 0:
		tmp.append(minimum["orig"]["str"] + "e\x2D1")
	elif minimum["orig"]["num"] < 0:
		tmp.append(minimum["orig"]["str"] + "e1")
	if maximum["orig"]["num"] > 0:
		tmp.append(maximum["orig"]["str"] + "e1")
	elif maximum["orig"]["num"] < 0:
		tmp.append(maximum["orig"]["str"] + "e\x2D1")
	return unique(tmp)

def spread(digit, separator):
	tmp = digit["scope"]
	decimal = ""
	if digit["type"] == "int":
		digit = digit["base"]["str"]
	elif digit["type"] == "float":
		const = "\x2E"
		array = digit["base"]["str"].split(const, 1)
		digit = array[0]
		decimal = const + array[1]
	for i in range(len(digit)):
		if i > 0:
			tmp += separator
		tmp += digit[i]
	tmp += decimal
	return tmp

def other(digit):
	# test bolean, empty, integer minimum, integer maximum, and other special values
	return unique([
		"true", "false",
		"1", "\x2D1", "\x2B1",
		"0", "\x2D0", "\x2B0", "0e\x2D1", "0e1",
		"null", "None", "nil",
		"An Array",
		spread(digit, "\x2C\x2C"),
		"%20%09" + digit["orig"]["str"], digit["orig"]["str"] + "%20%00%00",
		"\x2D2147483648", "2147483647", "4294967295",
		"\x2D2147483649", "2147483648", "4294967296"
	])

def fuzz(char, size, iterations, prepend = None, append = None):
	tmp = []
	for i in range(1, iterations + 1):
		string = char * size * i
		if prepend:
			string = prepend + string[len(prepend):]
		if append:
			string = string[:-len(append)] + append
		tmp.append(string)
	return unique(tmp)

def lengths():
	# test various lengths
	tmp = []
	for scope in ["", "\x2D"]:
		tmp.extend(fuzz("9", 128, 3, scope))
	return unique(tmp)

# ----------------------------------------

class Amounts:

	def __init__(self, minimum, maximum, middle, quotes):
		self.__minimum = minimum
		self.__maximum = maximum
		self.__middle  = middle
		self.__quotes  = quotes
		self.__amounts = []

	def run(self):
		for quotes in self.__quotes:
			tmp = []
			tmp.extend([self.__minimum["orig"]["str"], self.__maximum["orig"]["str"], self.__middle["orig"]["str"]])
			tmp.extend(separators(self.__middle))
			tmp.extend(zeros(self.__middle))
			tmp.extend(scopes(self.__middle))
			tmp.extend(currencies(self.__middle))
			tmp.extend(brackets(self.__middle, quotes))
			tmp.extend(flows(self.__minimum, self.__maximum))
			tmp.extend(notations(self.__minimum, self.__maximum, self.__middle))
			tmp.extend(other(self.__middle))
			tmp.extend(lengths())
			if quotes:
				tmp = [add_quotes(entry, quotes) for entry in tmp]
			self.__amounts.extend(tmp)
		return unique(self.__amounts)

# ----------------------------------------

class MyArgParser(argparse.ArgumentParser):

	def print_help(self):
		print("Amounts v3.3 ( github.com/ivan-sincek/amounts )")
		print("")
		print("--- Generate a wordlist from an amount range ---")
		print("Usage:   python3 amounts.py -min minimum -max maximum -mid middle -o out         [-q quotes]")
		print("Example: python3 amounts.py -min 1       -max 1000    -mid 20     -o amounts.txt [-q double]")
		print("")
		print("--- Generate a wordlist from a single amount ---")
		print("Usage:   python3 amounts.py -mid middle -o out         [-q quotes]")
		print("Example: python3 amounts.py -mid 20     -o amounts.txt [-q double]")
		print("")
		print("DESCRIPTION")
		print("    Generate a wordlist to fuzz amounts or any other numerical values")
		print("MINIMUM")
		print("    Minimum amount allowed")
		print("    If not specified, middle amount will be used")
		print("    -min, --minimum = 1 | etc.")
		print("MAXIMUM")
		print("    Maximum amount allowed")
		print("    If not specified, middle amount will be used")
		print("    -max, --maximum = 1000 | etc.")
		print("MIDDLE")
		print("    Preferably a multi-digit amount greater than minimum, lesser than maximum, and other than zero")
		print("    -mid, --middle = 20 | etc.")
		print("OUT")
		print("    Output file")
		print("    -o, --out = amounts.txt | etc.")
		print("QUOTES")
		print("    Enclose amounts in quotes")
		print("    Use comma-separated values")
		print("    -q, --quotes = original | single | double | backtick | all")

	def error(self, message):
		if len(sys.argv) > 1:
			print("Missing a mandatory option (-mid, -o) and/or optional (-min, -max, -q)")
			print("Use -h or --help for more info")
		else:
			self.print_help()
		exit()

class Validate:

	def __init__(self):
		self.__proceed = True
		self.__parser  = MyArgParser()
		self.__parser.add_argument("-min", "--minimum", required = False, type = str      , default = "")
		self.__parser.add_argument("-max", "--maximum", required = False, type = str      , default = "")
		self.__parser.add_argument("-mid", "--middle" , required = True , type = str      , default = "")
		self.__parser.add_argument("-o"  , "--out"    , required = True , type = str      , default = "")
		self.__parser.add_argument("-q"  , "--quotes" , required = False, type = str.lower, default = "")

	def run(self):
		self.__args = self.__parser.parse_args()
		self.__args.middle  = self.__parse_digit(self.__args.middle, "middle")   # required
		self.__args.minimum = self.__parse_digit(self.__args.minimum, "minimum") if self.__args.minimum else self.__args.middle
		self.__args.maximum = self.__parse_digit(self.__args.maximum, "maximum") if self.__args.maximum else self.__args.middle
		self.__args.quotes  = self.__parse_qoutes(self.__args.quotes)            if self.__args.quotes else self.__get_quote("original")
		self.__args         = vars(self.__args)
		return self.__proceed

	def get_arg(self, key):
		return self.__args[key]

	def __error(self, msg):
		self.__proceed = False
		self.__print_error(msg)

	def __print_error(self, msg):
		print(("ERROR: {0}").format(msg))

	def __parse_digit(self, value, target):
		target = target.capitalize()
		if is_int(value):
			value = parse_digit(value, "int")
		elif is_float(value):
			if len(value.split("\x2E", 1)[-1]) > 12:
				self.__error(("{0} amount cannot have more than 12 decimal places").format(target))
			else:
				value = parse_digit(value, "float")
		else:
			self.__error(("{0} amount must be either integer or float").format(target))
		return value

	def __parse_qoutes(self, value):
		tmp = []
		for entry in value.lower().split("\x2C"):
			entry = entry.strip()
			if not entry:
				continue
			elif entry not in ["original", "single", "double", "backtick", "all"]:
				self.__error("Supported quotes are 'original', 'single', 'double', 'backtick', or 'all'")
				break
			elif entry == "all":
				tmp.clear()
				tmp.extend(self.__get_quote(entry))
				break
			else:
				tmp.extend(self.__get_quote(entry))
		return unique(tmp)

	def __get_quote(self, value):
		if value == "original":
			return [""]
		elif value == "single":
			return ["\x27"]
		elif value == "double":
			return ["\x22"]
		elif value == "backtick":
			return ["\x60"]
		elif value == "all":
			return ["", "\x27", "\x22", "\x60"]

# ----------------------------------------

def main():
	validate = Validate()
	if validate.run():
		print("##########################################################################")
		print("#                                                                        #")
		print("#                              Amounts v3.3                              #")
		print("#                                 by Ivan Sincek                         #")
		print("#                                                                        #")
		print("# Generate a wordlist to fuzz amounts or any other numerical values.     #")
		print("# GitHub repository at github.com/ivan-sincek/amounts.                   #")
		print("# Feel free to donate ETH at 0xbc00e800f29524AD8b0968CEBEAD4cD5C5c1f105. #")
		print("#                                                                        #")
		print("##########################################################################")
		out = validate.get_arg("out")
		amounts = Amounts(
			validate.get_arg("minimum"),
			validate.get_arg("maximum"),
			validate.get_arg("middle"),
			validate.get_arg("quotes")
		)
		results = amounts.run()
		if results:
			write_array(results, out)

if __name__ == "__main__":
	main()
