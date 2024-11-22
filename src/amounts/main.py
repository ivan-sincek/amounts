#!/usr/bin/env python3

from .utils import array, config, digit, file, general, fuzz, validate

class Amounts:

	def __init__(self, minimum: digit.Amount, maximum: digit.Amount, middle: digit.Amount, quotes: list[general.Quote], ignore: bool):
		self.__minimum = minimum
		self.__maximum = maximum
		self.__middle  = middle
		self.__quotes  = quotes
		self.__ignore  = ignore

	def run(self):
		wordlist = []
		for quote in self.__quotes:
			tmp = []
			tmp.extend(fuzz.separators(self.__middle))
			tmp.extend(fuzz.zeros(self.__middle))
			tmp.extend(fuzz.scopes(self.__middle))
			tmp.extend(fuzz.currencies(self.__middle))
			tmp.extend(fuzz.brackets(self.__middle, quote, self.__ignore))
			tmp.extend(fuzz.flows(self.__minimum, self.__maximum, self.__ignore))
			tmp.extend(fuzz.notations(self.__minimum, self.__maximum, self.__middle, self.__ignore))
			tmp.extend(fuzz.other(self.__middle, self.__ignore))
			tmp.extend(fuzz.lengths(self.__ignore))
			for amount in [self.__minimum, self.__maximum, self.__middle]:
				if amount and amount.string in tmp:
					tmp.remove(amount.string)
					tmp.append(amount.string)
			wordlist.extend(tmp)
			if quote != general.Quote.NONE:
				wordlist.extend([fuzz.enquote(entry, quote.value) for entry in tmp])
		return array.unique(wordlist)

# ----------------------------------------

def main():
	(success, args) = validate.Validate().validate_args()
	if success:
		config.banner()
		amounts = Amounts(args.minimum, args.maximum, args.middle, args.quotes, args.ignore)
		results = amounts.run()
		if results:
			file.overwrite_array(results, args.out)

if __name__ == "__main__":
	main()
