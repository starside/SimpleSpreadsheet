import argparse
from enum import Enum
import re
import sys
import os

# Useful Enumerations
class TokenKind(Enum):
	NUMBER = 1
	CELL = 2
	OPERATION = 3
	ERROR = 4

class CellState(Enum):
	UNEVAL = 1
	STARTED = 2
	FINISHED = 3

# Some utility functions
def doOp(op, x, y):
	if op == "+":
		return x.value + y.value
	if op == "-":
		return x.value - y.value
	if op == "*":
		return x.value * y.value
	if op == "/":
		return x.value / y.value

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

def tokenizeString(input):
		""" Takes a postfix expression as string input.  Possible tokens
			are number, cell, and operation( + - * / ).  Returns array
			of tokens, which is also the cell's stack """
		raw = input.split() # splits words based on whitespace. Deletes empty

		# If empty, return number 0
		if len(raw) == 0:
			return [Token(0, TokenKind.NUMBER)]
		#Tokenize string
		result = [stringToToken(x) for x in raw]
		return result
		
# Classes
class Cell:
	def __init__(self, text):
		self.stack = tokenizeString(text)
		self.state = CellState.UNEVAL
		self.finalvalue = None

	def cellError(self):
		self.state = CellState.FINISHED
		self.finalvalue = Token(None, TokenKind.ERROR)
		return self.finalvalue

class Row:
	""" Class represents a row in the system """
	def __init__(self, text):
		""" Takes text input and returns a row"""
		cells = text.split(",")
		self.numCols = len(cells)
		self.cells = [Cell(x) for x in cells]

class Token:
	def __init__(self, value, kind):
		self.value = value
		self.kind = kind

	def toString(self):
		""" Quick function to convert token to printable string """
		if self.kind == TokenKind.ERROR:
			return "#ERR"
		return str(self.value)

class Sheet:
	def __init__(self, rows):
		""" Takes array of rows"""
		self.rows = rows

	def getCell(self, col, row):
		""" Get cell, both row and col start at 0 """
		if col >= 26 or col < 0: # Verify hard limits are enforced
			return None
		if row < 0:
			return None
		if row > len(self.rows) - 1:
			return None
		therow = self.rows[row]
		if col > therow.numCols - 1:
			return None
		return therow.cells[col]

	def evalCell(self, col, row):
		""" Evaluates a cell.  Returns a token.  This is a recursive call """
		cell = self.getCell(col, row)
		if cell is None:
			return Token(None, TokenKind.ERROR)

		if cell.state == CellState.FINISHED: # Do not recomupute cells
			return cell.finalvalue
		elif cell.state == CellState.STARTED: # Do not allow circular definitions
			return cell.cellError()
		cell.state = CellState.STARTED # Set cell state to started

		tokens = cell.stack
		tokens = tokens[::-1]
		stack = []
		while len(tokens) > 0:
			first = tokens.pop()
			if first.kind == TokenKind.OPERATION:
				try:
					left = stack.pop()
					right = stack.pop()
				except IndexError:
					return cell.cellError()
				if left.kind == TokenKind.ERROR or right.kind == TokenKind.ERROR:
					return cell.cellError()
				stack.append(Token(doOp(first.value, right, left), TokenKind.NUMBER) )
			elif first.kind == TokenKind.NUMBER:
				stack.append(first)
			elif first.kind == TokenKind.CELL:
				#eval cell
				c,r = first.value # Find cell address
				try:
					stack.append(self.evalCell(c,r))
				except RecursionError: # Make max recursion a defined case
					sys.stderr.write("Max recursion exceeded when entering cell " + str((c,r)) )
					return cell.cellError()
			else:
				return cell.cellError()
		if len(stack) != 1:
			return cell.cellError()
		res = stack.pop()
		cell.state = CellState.FINISHED
		cell.finalvalue = res
		return res

	def printResult(self, output):
		"""
		Print the calculated sheet results to the output stream.
		output should be a file descriptor, from open, sys.stdout,
		etc.
		"""
		for rowi, row in enumerate(self.rows):
			for coli, col in enumerate(row.cells):
				if coli > 25: # Ignore columns greater than z (26th character)
					break
				#Evaluate cell and write the output
				output.write( self.evalCell(coli, rowi).toString() )
				if coli < row.numCols - 1: # Do not print a trailing comma
					output.write(", ")
			output.write(os.linesep) # Windows/linux endline

# Main program invocation. 
if __name__ == "__main__":
	# Parse command line arguments
	parser = argparse.ArgumentParser(description='Compute a spreadsheet')
	parser.add_argument("inputfilename") # Input file name
	parser.add_argument("-o", "--outputfilename")
	args = parser.parse_args()

	rows = [] #Array of rows
	try:
		f = open(args.inputfilename)
	except:
		print("Could not open ./" + args.inputfilename + "!  Make sure it exists")
		exit(1)
	else: # Read in row and append to a list
		with f:
			for line in f:
				rows.append(Row(line))
	#Create sheet
	mainsheet = Sheet(rows)
	try:
		if args.outputfilename:
			output = open(args.outputfilename,'w')
		else:
			output = sys.stdout
	except:
		print("Could not open ./" + args.outputfilename + "!  Make sure it can be written")
		exit(1)
	else: # Generate output file
		with output:
			# Print result
			mainsheet.printResult(output)
