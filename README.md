# Amounts

Generate a wordlist to fuzz amounts or any other numerical values. Based on [Common Security Issues in Financially-Oriented Web Applications](https://research.nccgroup.com/wp-content/uploads/2020/07/common_security_issues_in_financially-orientated_web.pdf).

Bypass minimum and maximum restrictions, cause an unintended behavior and errors, etc.

Works with integer and float numerical values.

Tests:

* using amount separators such as space, dot, and comma;
* prepending zeros and appending decimal zeros using amount separators such as space and comma;
* prepending and appending positive and negative scope;
* prepending currency symbols such as `$`, `£`, and `€` - including negative scope;
* embracing the amount with brackets such as `()`, `[]`, and `{}` - and expanding it;
* trying underflows and overflows;
* trying binary, hexadecimal, hexadecimal ASCII, hexadecimal Unicode, and exponential notations;
* trying bolean, empty, integer minimum and maximum, and other special values,
* trying various lengths - including negative scope.

Pre-generated wordlists can be found in [/src/wordlists/](https://github.com/ivan-sincek/amounts/tree/main/src/wordlists); also a part of [/danielmiessler/SecLists/tree/master/Fuzzing/Amounts](https://github.com/danielmiessler/SecLists/tree/master/Fuzzing/Amounts).

Complimentary wordlists:

* [/danielmiessler/SecLists/blob/master/Fuzzing/JSON.Fuzzing.txt](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/JSON.Fuzzing.txt)

Extend this script to your liking.

Tested on Kali Linux v2023.4 (64-bit).

Made for educational purposes. I hope it will help!

## Table of Contents

* [How to Install](#how-to-install)
* [How to Build and Install Manually](#how-to-build-and-install-manually)
* [Generated Amounts](#generated-amounts)
* [Usage](#usage)

## How to Install

```fundamental
pip3 install --upgrade amounts
```

## How to Build and Install Manually

Run the following commands:

```fundamental
git clone https://github.com/ivan-sincek/amounts && cd amounts

python3 -m pip install --upgrade build

python3 -m build

python3 -m pip install dist/amounts-3.3-py3-none-any.whl
```

## Generated Amounts

```fundamental
amounts -min 1 -max 10000 -mid 2200 -o amounts.txt
```

`amounts.txt` generated wordlist:

```fundamental
1
10000
2200
2 200
2.200
2,200
002200
2200.00
2200,00
+2200
2200+
-2200
2200-
$2200
$-2200
-$2200
£2200
£-2200
-£2200
€2200
€-2200
-€2200
()
(,,)
(2200)
(2200,2201)
("2200")
("2200","2201")
[]
[,,]
[2200]
[2200,2201]
["2200"]
["2200","2201"]
{}
{,,}
{2200}
{2200,2201}
{"2200"}
{"2200","2201"}
0
10001
NaN
-NaN
Infinity
-Infinity
inf
-inf
0b100010011000
0x898
\x32\x32\x30\x30
\u0032\u0032\u0030\u0030
&h00
&hff
0.00000000000000000000000000000000000000000000000001
1e-50
2200e0
1e-1
10000e1
true
false
-1
+1
-0
+0
0e-1
0e1
null
None
nil
An Array
2,,2,,0,,0
%20%092200
2200%20%00%00
-2147483648
2147483647
4294967295
-2147483649
2147483648
4294967296
99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
-9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
-999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
-99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
```

## Usage

```fundamental
Amounts v3.3 ( github.com/ivan-sincek/amounts )

--- Generate a wordlist from an amount range ---
Usage:   python3 amounts.py -min minimum -max maximum -mid middle -o out         [-q quotes]
Example: python3 amounts.py -min 1       -max 1000    -mid 20     -o amounts.txt [-q double]

--- Generate a wordlist from a single amount ---
Usage:   python3 amounts.py -mid middle -o out         [-q quotes]
Example: python3 amounts.py -mid 20     -o amounts.txt [-q double]

DESCRIPTION
    Generate a wordlist to fuzz amounts or any other numerical values
MINIMUM
    Minimum amount allowed
    If not specified, middle amount will be used
    -min, --minimum = 1 | etc.
MAXIMUM
    Maximum amount allowed
    If not specified, middle amount will be used
    -max, --maximum = 1000 | etc.
MIDDLE
    Preferably a multi-digit amount greater than minimum, lesser than maximum, and other than zero
    -mid, --middle = 20 | etc.
OUT
    Output file
    -o, --out = amounts.txt | etc.
QUOTES
    Enclose amounts in quotes
    Use comma-separated values
    -q, --quotes = original | single | double | backtick | all
```
