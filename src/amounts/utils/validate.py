#!/usr/bin/env python3

from . import array, config, digit, general

import argparse, sys, typing

class MyArgParser(argparse.ArgumentParser):

	def print_help(self):
		print(f"Amounts {config.APP_VERSION} ( github.com/ivan-sincek/amounts )")
		print("")
		print("Usage:   amounts [-min minimum] [-max maximum] -mid middle -o out         [-q quotes]")
		print("Example: amounts [-min 1      ] [-max 1000   ] -mid 20     -o amounts.txt [-q double]")
		print("")
		print("DESCRIPTION")
		print("    Generate a wordlist to fuzz amounts or any other numerical values")
		print("MINIMUM")
		print("    Minimum amount allowed")
		print("    -min, --minimum = 1 | etc.")
		print("MAXIMUM")
		print("    Maximum amount allowed")
		print("    -max, --maximum = 1000 | etc.")
		print("MIDDLE")
		print("    Preferably, a multi-digit amount greater than the minimum, lesser than the maximum, and not equal to zero")
		print("    -mid, --middle = 20 | etc.")
		print("QUOTES")
		print("    Quotes for enclosing the amounts")
		print("    Use comma-separated values")
		print("    Default: none")
		print("    -q, --quotes = none | single | double | backtick | all")
		print("IGNORE")
		print("    Ignore hardcoded values")
		print("    -i, --ignore")
		print("OUT")
		print("    Output file")
		print("    -o, --out = amounts.txt | etc.")

	def error(self, message):
		if len(sys.argv) > 1:
			print("Missing a mandatory option (-mid, -o) and/or optional (-min, -max, -q)")
			print("Use -h or --help for more info")
		else:
			self.print_help()
		exit()

class Validate:

	def __init__(self):
		"""
		Class for validating and managing CLI arguments.
		"""
		self.__parser = MyArgParser()
		self.__parser.add_argument("-min", "--minimum", required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-max", "--maximum", required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-mid", "--middle" , required = True , type   = str         , default = ""   )
		self.__parser.add_argument("-q"  , "--quotes" , required = False, type   = str.lower   , default = ""   )
		self.__parser.add_argument("-i"  , "--ignore" , required = False, action = "store_true", default = False)
		self.__parser.add_argument("-o"  , "--out"    , required = True , type   = str         , default = ""   )

	def validate_args(self):
		"""
		Validate and return the CLI arguments.
		"""
		self.__success = True
		self.__args = self.__parser.parse_args()
		self.__validate_minimum()
		self.__validate_maximum()
		self.__validate_middle()
		self.__validate_quotes()
		return self.__success, self.__args

	def __error(self, message: str):
		"""
		Set the success flag to 'False' to prevent the main task from executing, and print an error message.
		"""
		self.__success = False
		general.print_error(message)

	# ------------------------------------

	def __is_amount(self, arg: typing.Any):
		return isinstance(arg, digit.Amount)

	def __validate_minimum(self):
		if self.__args.minimum:
			self.__args.minimum, message = digit.validate_minimum(self.__args.minimum)
			if message:
				self.__error(message)
			elif self.__is_amount(self.__args.maximum) and self.__args.minimum.numeric > self.__args.maximum.numeric:
				self.__error("Minimum amount must be lesser than or equal to maximum amount")
		else:
			self.__args.minimum = None

	def __validate_maximum(self):
		if self.__args.maximum:
			self.__args.maximum, message = digit.validate_maximum(self.__args.maximum)
			if message:
				self.__error(message)
			elif self.__is_amount(self.__args.minimum) and self.__args.maximum.numeric < self.__args.minimum.numeric:
				self.__error("Maximum amount must be greater than or equal to minimum amount")
		else:
			self.__args.maximum = None

	def __validate_middle(self):
		self.__args.middle, message = digit.validate_middle(self.__args.middle)
		if message:
			self.__error(message)
		elif self.__is_amount(self.__args.minimum) and self.__args.middle.numeric < self.__args.minimum.numeric:
			self.__error("Middle amount must be greater than or equal to minimum amount")
		elif self.__is_amount(self.__args.maximum) and self.__args.middle.numeric > self.__args.maximum.numeric:
			self.__error("Middle amount must be lesser than or equal to maximum amount")

	def __validate_quotes(self):
		if self.__args.quotes:
			types = array.remove_empty_strings(self.__args.quotes.split(","))
			self.__args.quotes = []
			if not types:
				self.__error("No quotes were specified")
			else:
				supported = [type.value for type in general.Quote.types()]
				for type in types:
					if type == "all":
						self.__args.quotes.extend(general.Quote.all())
					elif type not in supported:
						self.__error("Supported quotes are 'none', 'single', 'double', 'backtick', or 'all'")
						break
					else:
						self.__args.quotes.append(general.Quote.get(type))
				self.__args.quotes = array.unique(self.__args.quotes)
		else:
			self.__args.quotes = [general.Quote.NONE]
