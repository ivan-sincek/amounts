#!/usr/bin/env python3

import os

ENCODING = "UTF-8"

def overwrite_array(array: list[str], out: str):
	"""
	Write a list to an output file.\n
	If the output file exists, prompt to overwrite it.
	"""
	confirm = "yes"
	if os.path.isfile(out):
		print(f"'{out}' already exists")
		confirm = input("Overwrite the output file (yes): ")
	if confirm.lower() in ["yes", "y"]:
		try:
			open(out, "w", encoding = ENCODING).write(("\n").join(array))
			print(f"Results have been saved to '{out}'")
		except Exception as ex:
			print(f"Cannot save the results to '{out}'")
