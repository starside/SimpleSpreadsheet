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

# Breaking down the code

This section describes how the code works.

## Tokenizer

I wrote a very simple tokenizer, that converts a string to a token.  Internally a token is a class with two fields, value and kind.  Value is the value of the token, and kind is the type of token.

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
            
As can be seen from the code above, the kind field is specified by an enumeration from the class TokenKind.  NUMBER and OPERATION describe a number or an arithmetic operation.  CELL means a cell reference in {LETTER}{NUMBER} format, and ERROR is an invalid token.  The heart of the tokenizer is a function called stringToToken, which when given a string returns a single token.

stringToToken classifies tokens using a finite state machine.  Python's regular expression engine is a state machine, and well suited to tokenizing string.  The regular expression that does the heavy lifting is 

    def stringToToken(input):
		""" Takes a string with stripped whitespace and
			returns a token. """
		# Empty tokens should not occur
		if len(input) == 0:
			return Token(None, TokenKind.ERROR)
		# Create regex based state machine to tokenize
		scanner = re.compile(r'''
			(^([A-Za-z])([0-9]+)$) |# Match a cell
			(^[+*/\-]$)	|			# Match an op
			(^[0-9]+[.]*[0-9]*$)	# Match a number
		''', re.VERBOSE)
		# Match regex to input string
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
    
The above regex matches either a cell reference, operation or a nuber, and returns the result as a match with five groups.  By inspecting the value of these groups, I determine the type of token.  If no match is found, and error token is returned.  The code below performs this calculation:

    # Match regex to input string
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

Internally the program operates recusively.  evalCell does the actual evaluation
of a cell.  If it encounters a cell reference, like b2, it will recursively 
evaluate cell b2.  Cells are marked with a cell state.  The reason is if
evalCell encounters a cell that has not finished calculating its value, it
means a circular definition exists.  This results in an error.

For example, the input:

input.csv:
>b1,a1
>b2 1 +,1

will return:

output.csv:
>#ERR, #ERR
>2.0, 1.0

Cells also record their final numeric value, so if a cell is referenced multiple
times it does not need to recomute the result.

Another way to solve this is a topological sort, to determine the order of cell
calculation.  However I chose recursive because I felt like it was more idiot
proof in the time limits.

I include a sample input.csv.

I developed this program on windows.  Should be fine on linux and mac.
