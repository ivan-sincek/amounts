#!/usr/bin/env python3

import sys
import os
import re
import struct

# -------------------------- INFO --------------------------

def basic():
	global proceed
	proceed = False
	print("Amounts v2.2 ( github.com/ivan-sincek/amounts )")
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
	print("    Use comma separated values")
	print("    -q <quotes> - original | single | double | backtick | all")

# ------------------- MISCELENIOUS BEGIN -------------------

def unique(sequence):
	seen = set()
	return [x for x in sequence if not (x in seen or seen.add(x))]

def is_int(string):
	return re.match(r"^[\-]{0,1}\d+$", string) is not None

def is_float(string):
	return re.match(r"^[\-]{0,1}\d+[\.]{0,1}\d+$", string) is not None

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
	const = "-"
	if string[0] == const:
		tmp["scope"] = const
	if parse == "int":
		tmp["orig"]["num"] = int(string)
		tmp["orig"]["str"] = str(tmp["orig"]["num"])
	elif parse == "float":
		tmp["orig"]["num"] = float(string)
		tmp["orig"]["str"] = ("{0:.12f}").format(tmp["orig"]["num"]).rstrip("0")
	tmp["base"]["str"] = tmp["orig"]["str"].lstrip(const)
	return tmp

def parse_comma_values(string, values):
	tmp = []
	array = string.split(",")
	for entry in array:
		entry = entry.strip()
		if entry:
			if entry == "all":
				tmp = ["all"]
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
		if entry == "all":
			tmp = ["", "\x27", "\x22", "\x60"]
			break
		elif entry == "original":
			tmp.append("")
		elif entry == "single":
			tmp.append("\x27")
		elif entry == "double":
			tmp.append("\x22")
		elif entry == "backtick":
			tmp.append("\x60")
	return unique(tmp)

def separate(digit, separator, skip = 3):
	scope = digit["scope"]
	decimal = ""
	if digit["type"] == "int":
		digit = digit["base"]["str"][::-1]
	elif digit["type"] == "float":
		const = "."
		array = digit["base"]["str"].split(const)
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
		return "0b" + format(struct.unpack("!I", struct.pack("!f", digit["orig"]["num"]))[0], "032b")

def to_hex(digit):
	if digit["type"] == "int":
		return hex(digit["orig"]["num"])
	elif digit["type"] == "float":
		return float.hex(digit["orig"]["num"])

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

args = {"minimum": None, "maximum": None, "mid": None, "amount": None, "out": None, "quotes": None}

def validate_digit(value, text):
	text = text.capitalize()
	if is_int(value):
		value = parse_digit(value, "int")
	elif is_float(value):
		if len(value.split(".")[1]) > 12:
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
		elif key == "-mid" and args["mid"] is None:
			args["mid"] = validate_digit(value, "middle")
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
	if (args["amount"] and (args["minimum"] is not None or args["maximum"] is not None or args["mid"] is not None)) or (not args["amount"] and (args["minimum"] is None or args["maximum"] is None or args["mid"] is None)) or args["out"] is None or not check(argc, args):
		error("Missing a mandatory option (-min, -max, -mid, -o) and/or optional (-q)")
		error("Missing a mandatory option (-a, -o) and/or optional (-q)", True)
else:
	error("Incorrect usage", True)

# --------------------- VALIDATION END ---------------------

# ----------------------- TASK BEGIN -----------------------

def separators(digit):
	# test amount separators
	tmp = []
	for separator in [" ", ".", ","]:
		tmp.append(separate(digit, separator))
	return unique(tmp)

def zeros(digit):
	# test prepending zeros and appending decimal zeros
	zeros = "0" * 2
	tmp = [
		digit["scope"] + zeros + digit["base"]["str"]
	]
	for separator in [".", ","]:
		if digit["type"] == "int":
			tmp.append(digit["orig"]["str"] + separator + zeros)
		elif digit["type"] == "float":
			tmp.append(digit["orig"]["str"].replace(".", separator))
	return unique(tmp)

def scopes(digit):
	# test prepending and appending scopes
	tmp = []
	for scope in ["", "+", "-"]:
		tmp.extend([scope + digit["base"]["str"], digit["base"]["str"] + scope])
	return unique(tmp)

def currencies(digit):
	# test prepending currency symbols - including scopes
	tmp = []
	# $, £, €
	for currency in ["\x24", "\xA3", "\u20AC"]:
		for scope in ["", "-"]:
			tmp.extend([currency + scope + digit["base"]["str"], scope + currency + digit["base"]["str"]])
	return unique(tmp)

def brackets(digit, quotes):
	# test embracing amount with brackets and expanding
	tmp = []
	if not quotes:
		quotes = "\x22"
	separator = ","
	for placeholder in ["(X)", "[X]", "{X}"]:
		tmp.extend([
			placeholder.replace("X", ""),
			placeholder.replace("X", separator * 2),
			placeholder.replace("X", digit["orig"]["str"]),
			placeholder.replace("X", digit["orig"]["str"] + separator + increment(digit)),
			placeholder.replace("X", add_quotes(digit["orig"]["str"], quotes)),
			placeholder.replace("X", add_quotes(digit["orig"]["str"], quotes) + separator + add_quotes(increment(digit), quotes))
		])
	return unique(tmp)

def flows(minimum, maximum):
	# test underflows and overflows
	tmp = [
		decrement(minimum),
		increment(maximum)
	]
	for value in ["NaN", "Infinity", "inf"]:
		for scope in ["", "-"]:
			tmp.append(scope + value)
	return unique(tmp)

def notations(minimum, maximum, mid):
	# test binary, hexadecimal, and exponential notations
	tmp = [
		to_bin(mid),
		to_hex(mid),
		"&h00", "&hff",
		"0.00000000000000000000000000000000000000000000000001", "1e-50",
		mid["orig"]["str"] + "e0"
	]
	if minimum["orig"]["num"] > 0:
		tmp.append(minimum["orig"]["str"] + "e-1")
	elif minimum["orig"]["num"] < 0:
		tmp.append(minimum["orig"]["str"] + "e1")
	if maximum["orig"]["num"] > 0:
		tmp.append(maximum["orig"]["str"] + "e1")
	elif maximum["orig"]["num"] < 0:
		tmp.append(maximum["orig"]["str"] + "e-1")
	return unique(tmp)

def spread(digit, separator):
	tmp = digit["scope"]
	decimal = ""
	if digit["type"] == "int":
		digit = digit["base"]["str"]
	elif digit["type"] == "float":
		const = "."
		array = digit["base"]["str"].split(const)
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
		"1", "-1", "+1",
		"0", "-0", "+0",
		"null", "None", "nil",
		"An Array",
		spread(digit, ",,"),
		"%20%09" + digit["orig"]["str"], digit["orig"]["str"] + "%20%00%00",
		"-2147483648", "2147483647", "4294967295",
		"-2147483649", "2147483648", "4294967296"
	])

def lengths():
	# test various lengths
	tmp = []
	for scope in ["", "-"]:
		tmp.extend(fuzz("9", 128, 3, scope))
	return unique(tmp)

def generate(minimum, maximum, mid, quotes = None):
	amounts = []
	amounts.extend([minimum["orig"]["str"], maximum["orig"]["str"], mid["orig"]["str"]])
	amounts.extend(separators(mid))
	amounts.extend(zeros(mid))
	amounts.extend(scopes(mid))
	amounts.extend(currencies(mid))
	amounts.extend(brackets(mid, quotes))
	amounts.extend(flows(minimum, maximum))
	amounts.extend(notations(minimum, maximum, mid))
	amounts.extend(other(mid))
	amounts.extend(lengths())
	if quotes:
		amounts = [add_quotes(amount, quotes) for amount in amounts]
	return unique(amounts)

if proceed:
	print("######################################################################")
	print("#                                                                    #")
	print("#                            Amounts v2.2                            #")
	print("#                               by Ivan Sincek                       #")
	print("#                                                                    #")
	print("# Generate a wordlist to fuzz amounts or any other numerical values. #")
	print("# GitHub repository at github.com/ivan-sincek/amounts.               #")
	print("# Feel free to donate bitcoin at 1BrZM6T7G9RN8vbabnfXu4M6Lpgztq6Y14. #")
	print("#                                                                    #")
	print("######################################################################")
	if args["amount"]:
		args["minimum"] = args["amount"]
		args["maximum"] = args["amount"]
		args["mid"] = args["amount"]
	if not args["quotes"]:
		args["quotes"] = [""]
	collection = []
	for quotes in args["quotes"]:
		collection.extend(generate(args["minimum"], args["maximum"], args["mid"], quotes))
	write_file(unique(collection), args["out"])

# ------------------------ TASK END ------------------------
