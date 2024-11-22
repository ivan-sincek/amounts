# Amounts

Generate a wordlist to fuzz amounts or any other numerical values. Based on [Common Security Issues in Financially-Oriented Web Applications](https://soroush.me/downloadable/common-security-issues-in-financially-orientated-web-applications.pdf).

Bypass minimum and maximum restrictions, cause an unintended behavior and errors, etc.

Works with integer and float numerical values.

Tests:

* Grouping and separating digits using separators such as space, comma, and dot.
* Adding leading zeros and trailing decimal zeros using separators such as space and comma.
* Prepending and appending negative and positive scope.
* Prepending fiat currency symbols such as `$`, `£`, and `€` with and without negative and positive scope.
* Adding brackets such as `()`, `[]`, and `{}` and extending the inner elements.
* Testing overflows, underflows, and infinite values.
* Testing binary and hexadecimal representations, exponential notations, and byte and Unicode escape sequences.
* Testing boolean, empty, integer minimum, integer maximum, and other special values.
* Testing lengths.

Pre-generated wordlists can be found in [/src/wordlists/](https://github.com/ivan-sincek/amounts/tree/main/src/wordlists) and also a part of [/danielmiessler/SecLists/tree/master/Fuzzing/Amounts](https://github.com/danielmiessler/SecLists/tree/master/Fuzzing/Amounts).

Complimentary wordlists:

* [/danielmiessler/SecLists/blob/master/Fuzzing/JSON.Fuzzing.txt](https://github.com/danielmiessler/SecLists/blob/master/Fuzzing/JSON.Fuzzing.txt)

Tested on Kali Linux v2024.2 (64-bit).

Made for educational purposes. I hope it will help!

## Table of Contents

* [How to Install](#how-to-install)
	* [Standard Install](#standard-install)
	* [Build and Install From the Source](#build-and-install-from-the-source)
* [Generate Amounts](#generate-amounts)
* [Usage](#usage)

## How to Install

### Standard Install

```fundamental
pip3 install --upgrade amounts
```

### Build and Install From the Source

```fundamental
git clone https://github.com/ivan-sincek/amounts && cd amounts

python3 -m pip install --upgrade build

python3 -m build

python3 -m pip install dist/amounts-4.2-py3-none-any.whl
```

## Generate Amounts

```fundamental
amounts -min 1 -max 10000 -mid 2200 -o amounts.txt
```

Generate wordlist:

```fundamental
2 200
2,200
2.200
002200
2200,00
2200.00
-2200
2200-
+2200
2200+
2200
$-2200
-$2200
$+2200
+$2200
$2200
€-2200
-€2200
€+2200
+€2200
€2200
£-2200
-£2200
£+2200
+£2200
£2200
()
(,,)
(2200)
("2200")
(2200,2199)
("2200","2199")
[]
[,,]
[2200]
["2200"]
[2200,2199]
["2200","2199"]
{}
{,,}
{2200}
{"2200"}
{2200,2199}
{"2200","2199"}
0
10001
-NaN
-Infinity
-inf
NaN
Infinity
inf
0b100010011000
0x898
\x32\x32\x30\x30
\u0032\u0032\u0030\u0030
2200e0
2200e-50
0.00000000000000000000000000000000000000000000002200
1e-1
10000e1
&h00
&hff
2,,2,,0,,0
%20%092200
2200%20%00%00
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
-2147483648
2147483647
-2147483649
2147483648
4294967295
4294967296
99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
-9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
-999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
-99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
1
```

## Usage

```fundamental
Amounts v4.2 ( github.com/ivan-sincek/amounts )

Usage:   amounts [-min minimum] [-max maximum] -mid middle -o out         [-q quotes]
Example: amounts [-min 1      ] [-max 1000   ] -mid 20     -o amounts.txt [-q double]

DESCRIPTION
    Generate a wordlist to fuzz amounts or any other numerical values
MINIMUM
    Minimum amount allowed
    -min, --minimum = 1 | etc.
MAXIMUM
    Maximum amount allowed
    -max, --maximum = 1000 | etc.
MIDDLE
    Preferably, a multi-digit amount greater than the minimum, lesser than the maximum, and not equal to zero
    -mid, --middle = 20 | etc.
QUOTES
    Quotes for enclosing the amounts
    Use comma-separated values
    Default: none
    -q, --quotes = none | single | double | backtick | all
IGNORE
    Ignore hardcoded values
    -i, --ignore
OUT
    Output file
    -o, --out = amounts.txt | etc.
```
