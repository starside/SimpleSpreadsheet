# Simple Spreadsheet

This is a command line spreadsheet evaluator that uses postfix notation.  It was originally a homework assignment for a company interview, and I think it is a cute little problem, so I am posting it online with a breakdown of the code.  Cells accept postfix notation, so instead of writing 2 + 2, you should write 2 2 +.

Note that there was no request, explicit or implied to keep this problem confidential.  However I will keep the issuing company anonymous.

# Original Problem Statement

The original problem statement is paraphrased as follows:
Write a program that evaluates a CSV (Comma seperated value) file as a spreadsheet, with the following requirements:
1. Cells may be postfix expressions
2. Tokens in cells are seperated by whitespace
3. The four basic arithmetic operations, + - * /, are allowed
4. Cells are referred to in {LETTER}{NUMBER} notation.  For example, A4 refers to colum 1, row 4.  In my implementation, columns are not case sensitive. Cells have a default value of 0, if they exist in the csv.

# Running the Code
To invoke the program, run (using python 3):

    python spreadsheet_improved.py input.csv
    
The above command will output the results to stdout.  Optionally output can be written to a file using:

    python spreadsheet_improved.py input.csv -o output.csv

A sample input file could be:

    c3 b1 +, 3 c1 *, 3, +
    a1 1 +, 1 8 /, 2 3 -, sadf
    12, b2, 45, d3, , e3 1 *
    
With an expected output of 

    54.0, 9.0, 3.0, #ERR
    55.0, 0.125, -1.0, #ERR
    12.0, 0.125, 45.0, #ERR, 0, 0.0


I constrain the input to 26 columns, as I restrict column references from a to z,
and do not allow compund addressing.  Columns are not case sensitive.

Floating point and positive integers are valid inputs as numbers.  Ints are
internally converted to float for all operations.  Negative numbers are not
allowed.  To get negative numbers, use an expression like "0 7 -"

# Running tests

I included some unit tests the ensure certain specifications are met.  I do not aim for 100% code coverage, instead I check bounds, important error state and basic operations are correct.  Simple run

```
python test.py
```

# Breaking down the code

This section describes how the code works. Reference spreadsheet_improved.py to follow this section.

## Tokenizer

I wrote a very simple tokenizer, that converts a string to a token.  Internally a token is a class with two fields, value and kind.  Value is the value of the token, and kind is the type of token.

```python
    class TokenKind(Enum):
	    NUMBER = 1
	    CELL = 2
	    OPERATION = 3
	    ERROR = 4
    
    class Token:
	    def __init__(self, value, kind):
		    self.value = value
		    self.kind = kind

	    def toString(self):
		    """ Quick function to convert token to printable string """
		    if self.kind == TokenKind.ERROR:
		    	return "#ERR"
		    return str(self.value)
```
            
As can be seen from the code above, the kind field is specified by an enumeration from the class TokenKind.  NUMBER and OPERATION describe a number or an arithmetic operation.  CELL means a cell reference in {LETTER}{NUMBER} format, and ERROR is an invalid token.  The heart of the tokenizer is a function called stringToToken, which when given a string returns a single token.

stringToToken classifies tokens using a finite state machine.  Python's regular expression engine is a state machine, and well suited to tokenizing string.  The regular expression that does the heavy lifting is 

```python
scanner = re.compile(r'''
		(^([A-Za-z])([0-9]+)$) |# Match a cell
		(^[+*/\-]$)	|			# Match an op
		(^[0-9]+[.]*[0-9]*$)	# Match a number
	''', re.VERBOSE)
```
    
The above regex matches either a cell reference, operation or a nuber, and returns the result as a match with five groups.  By inspecting the value of these groups, I determine the type of token, which is done just below the regex, and lookes like:

```python
res = re.match(scanner, input)
	# Discover the token type
	if res is not None: # Found a valid token
		cell, col, row, op, num = res.groups()
		if cell: # A cell reference, ie A7
			rownum = int(row)
			# Is positive and zero?
			if rownum < 1:
				return Token(None, TokenKind.ERROR)
			colnum = ord(col.lower()) - ord('a') # Convert column letter to number
			return Token((colnum, rownum - 1), TokenKind.CELL)
		elif op:
			return Token(input, TokenKind.OPERATION)
		elif num:
			number = float(input) # Convert all #s to floating point
			return Token(number, TokenKind.NUMBER)
	# Could not convert, return error
	return Token(None, TokenKind.ERROR)
```

## Evaluating the spreadsheet

Internally the program operates recusively.  A method in Sheet called evalCell does the actual evaluation of a cell.  If it encounters a cell reference, like b2, it will recursively evaluate cell b2.  Cells are marked with a cell state.  The reason is if evalCell encounters a cell that has not finished calculating its value, it means a circular definition exists.  This results in an error.  There is a recursion limit in python, and the code detects any attempt exceed the recursion limit, returning an #ERR value in the cell.

For example, the input:

input.csv:

    b1,a1
    b2 1 +,1
    
will result in

    #ERR, #ERR
    2.0, 1.0

Cells also record their final numeric value, so if a cell is referenced multiple times it does not need to recompute the result.

Another way to solve this is a topological sort, to determine the order of cell calculation.  However I chose recursive because of the simplicity.  The sort would mean when a CELL token is encountered, its value can directly be substitued in to the evaluation. 

## Evaluating postfix expressions

This setion assumes knowledge of the common algorithms for evaluating postfix notation, I do not do a complete tutorial. There are two ways to evaluate a postfix expression (see Wikipedia for the two different algorithms).  evalCell uses left to right, meaning it encounters the operands before the operator.  This means I only need to recursively evaluate CELL tokens when they are first encountered in the token stream, and not when they are popped off the stack due to an operator.

It is also possible to use a right to left algorithm, and suggests a way to make evalCell non-recursive.  When an unevaluated cell token is encountered, remove it from the input token stream, and push the contents of its cell to the front of the stream.  For example if evaluating the expression `1 x +` and `x = 1 2 *`, then when x is read from the toke stream, just push `1 2 *` to get:

    `1 1 2 *`
    
Evaluation will proceed as expected.  Difficulties arise in preventing infintite loops, which is easy enough to fix.  Storing values of already computed cells is less easy to fix, and I have not implemented it.  The recursive solution is more efficient in the sense that it does not need to compute the value of a cell more than once, but it does have recursion limits and overhead.

I include a sample input.csv.

I developed this program on windows.  Should be fine on linux and mac.
