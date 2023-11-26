#!/usr/bin/env python3

import sys
import os
import re
import struct

# -------------------------- INFO --------------------------

def basic():
	global proceed
	proceed = False
	print("Amounts v3.2 ( github.com/ivan-sincek/amounts )")
	print("")
	print("--- Generate a wordlist for a range of amounts ---")
	print("Usage:   python3 amounts.py -min minimum -max maximum -mid middle -o out         [-q quotes]")
	print("Example: python3 amounts.py -min 1       -max 1000    -mid 20     -o amounts.txt [-q double]")
	print("")
	print("--- Generate a wordlist for a single amount ---")
	print("Usage:   python3 amounts.py -a amount -o out         [-q quotes]")
	print("Example: python3 amounts.py -a 20     -o amounts.txt [-q double]")

def advanced():
	basic()
	print("")
	print("DESCRIPTION")
	print("    Generate a wordlist to fuzz amounts or any other numerical values")
	print("MINIMUM")
	print("    Minimum amount allowed")
	print("    -min <minimum> - 1 | etc.")
	print("MAXIMUM")
	print("    Maximum amount allowed")
	print("    -max <maximum> - 1000 | etc.")
	print("MIDDLE")
	print("    Amount greater than minimum, lesser than maximum, and other than zero")
	print("    Preferably a multi-digit value")
	print("    -mid <middle> - 20 | etc.")
	print("AMOUNT")
	print("    Single amount")
	print("    Preferably a multi-digit value")
	print("    -a <amount> - 20 | etc.")
	print("OUT")
	print("    Output file")
	print("    -o <out> - amounts.txt | etc.")
	print("QUOTES")
	print("    Embrace amounts in quotes")
	print("    Use comma-separated values")
	print("    -q <quotes> - original | single | double | backtick | all")

# ------------------- MISCELENIOUS BEGIN -------------------

def is_int(string):
	return re.match(r"^[\-]{0,1}\d+$", string)

def is_float(string):
	return re.match(r"^[\-]{0,1}\d+[\.]{0,1}\d+$", string)

def parse_digit(string, parse):
	tmp = {
		"type": parse,
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
	if parse == "int":
		tmp["orig"]["num"] = int(string)
		tmp["orig"]["str"] = str(tmp["orig"]["num"])
	elif parse == "float":
		tmp["orig"]["num"] = float(string)
		tmp["orig"]["str"] = ("{0:.12f}").format(tmp["orig"]["num"]).rstrip("0")
	tmp["base"]["str"] = tmp["orig"]["str"].lstrip(const)
	return tmp

def unique(sequence):
	seen = set()
	return [x for x in sequence if not (x in seen or seen.add(x))]

def parse_comma_values(string, values):
	tmp = []
	for entry in string.split("\x2C"):
		entry = entry.strip()
		if not entry:
			continue
		elif entry == "all": # all
			tmp = [entry]
			break
		elif entry not in values:
			tmp = []
			break
		else:
			tmp.append(entry)
	return unique(tmp)

def fetch_quotes(array):
	tmp = []
	for entry in array:
		if entry == "original":
			tmp.append("")
		elif entry == "single":
			tmp.append("\x27")
		elif entry == "double":
			tmp.append("\x22")
		elif entry == "backtick":
			tmp.append("\x60")
		elif entry == "all":
			tmp = ["", "\x27", "\x22", "\x60"]
			break
	return unique(tmp)

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

def increment(digit, value = 1):
	return str(digit["orig"]["num"] + value)

def decrement(digit, value = 1):
	return str(digit["orig"]["num"] - value)

def to_bin(digit):
	if digit["type"] == "int":
		return bin(digit["orig"]["num"])
	elif digit["type"] == "float":
		# binary representation of a float number
		# v1
		return "0b" + format(struct.unpack("!I", struct.pack("!f", digit["orig"]["num"]))[0], "032b")
		# v2
		# return "0b" + ("").join([("{0:0>8b}").format(char) for char in struct.pack("!f", digit)])

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

def add_quotes(string, quotes):
	return quotes + string.replace(quotes, "\\" + quotes) + quotes

def write_file(array, out):
	with open(out, "w") as stream:
		for entry in array:
			stream.write(str(entry) + "\n")
	stream.close()
	print(("{0} results have been saved to '{1}'").format(len(array), out))

# -------------------- MISCELENIOUS END --------------------

# -------------------- VALIDATION BEGIN --------------------

# my own validation algorithm

proceed = True

def print_error(msg):
	print(("ERROR: {0}").format(msg))

def error(msg, help = False):
	global proceed
	proceed = False
	print_error(msg)
	if help:
		print("Use -h for basic and --help for advanced info")

args = {"minimum": None, "maximum": None, "middle": None, "amount": None, "out": None, "quotes": None}

def validate_digit(value, text):
	text = text.capitalize()
	if is_int(value):
		value = parse_digit(value, "int")
	elif is_float(value):
		if len(value.split("\x2E", 1)[0]) > 12:
			error(("{0} amount cannot have more than 12 decimal places").format(text))
		else:
			value = parse_digit(value, "float")
	else:
		error(("{0} amount must be an integer or float").format(text))
	return value

def validate(key, value):
	global args
	value = value.strip()
	if len(value) > 0:
		if key == "-min" and args["minimum"] is None:
			args["minimum"] = validate_digit(value, "minimum")
		elif key == "-max" and args["maximum"] is None:
			args["maximum"] = validate_digit(value, "maximum")
		elif key == "-mid" and args["middle"] is None:
			args["middle"] = validate_digit(value, "middle")
		elif key == "-a" and args["amount"] is None:
			args["amount"] = validate_digit(value, "single")
		elif key == "-o" and args["out"] is None:
			args["out"] = value
		elif key == "-q" and args["quotes"] is None:
			args["quotes"] = parse_comma_values(value.lower(), ["original", "single", "double", "backtick", "all"])
			if not args["quotes"]:
				error("Supported quotes are 'original', 'single', 'double', 'backtick', or 'all'")
			else:
				args["quotes"] = fetch_quotes(args["quotes"])

def check(argc, args):
	count = 0
	for key in args:
		if args[key] is not None:
			count += 1
	return argc - count == argc / 2

# --------------------- VALIDATION END ---------------------

# ----------------------- TASK BEGIN -----------------------

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

def lengths():
	# test various lengths
	tmp = []
	for scope in ["", "\x2D"]:
		tmp.extend(fuzz("9", 128, 3, scope))
	return unique(tmp)

def generate(minimum, maximum, middle, quotes = ""):
	amounts = []
	amounts.extend([minimum["orig"]["str"], maximum["orig"]["str"], middle["orig"]["str"]])
	amounts.extend(separators(middle))
	amounts.extend(zeros(middle))
	amounts.extend(scopes(middle))
	amounts.extend(currencies(middle))
	amounts.extend(brackets(middle, quotes))
	amounts.extend(flows(minimum, maximum))
	amounts.extend(notations(minimum, maximum, middle))
	amounts.extend(other(middle))
	amounts.extend(lengths())
	if quotes:
		amounts = [add_quotes(amount, quotes) for amount in amounts]
	return unique(amounts)

def main():
	argc = len(sys.argv) - 1

	if argc == 0:
		advanced()
	elif argc == 1:
		if sys.argv[1] == "-h":
			basic()
		elif sys.argv[1] == "--help":
			advanced()
		else:
			error("Incorrect usage", True)
	elif argc % 2 == 0 and argc <= len(args) * 2:
		for i in range(1, argc, 2):
			validate(sys.argv[i], sys.argv[i + 1])
		if (args["amount"] and (args["minimum"] is not None or args["maximum"] is not None or args["middle"] is not None)) or (not args["amount"] and (args["minimum"] is None or args["maximum"] is None or args["middle"] is None)) or args["out"] is None or not check(argc, args):
			error("Missing a mandatory option (-min, -max, -mid, -o) and/or optional (-q)")
			error("Missing a mandatory option (-a, -o) and/or optional (-q)", True)
	else:
		error("Incorrect usage", True)

	if proceed:
		print("##########################################################################")
		print("#                                                                        #")
		print("#                              Amounts v3.2                              #")
		print("#                                 by Ivan Sincek                         #")
		print("#                                                                        #")
		print("# Generate a wordlist to fuzz amounts or any other numerical values.     #")
		print("# GitHub repository at github.com/ivan-sincek/amounts.                   #")
		print("# Feel free to donate ETH at 0xbc00e800f29524AD8b0968CEBEAD4cD5C5c1f105. #")
		print("#                                                                        #")
		print("##########################################################################")
		if args["amount"]:
			args["minimum"] = args["maximum"] = args["middle"] = args["amount"]
		if not args["quotes"]:
			args["quotes"] = [""]
		collection = []
		for quotes in args["quotes"]:
			collection.extend(generate(args["minimum"], args["maximum"], args["middle"], quotes))
		write_file(unique(collection), args["out"])

if __name__ == "__main__":
	main()

# ------------------------ TASK END ------------------------
