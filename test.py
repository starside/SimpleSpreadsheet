import unittest
import sys
import io
from spreadsheet_improved import *

def evalSheet(inputText):
	rows = []
	for line in inputText:
		rows.append(Row(line))
	return Sheet(rows)

class TestTokenizer(unittest.TestCase):
	def test_tokenizer(self):
		""" Test some key cases for the tokenizer """
		err = TokenKind.ERROR
		num = TokenKind.NUMBER
		cel = TokenKind.CELL
		op = TokenKind.OPERATION
		inputs = ["0","1","-1","0.","0.0","45.0","43.0a","aa","a13","A12","a1.0","aa10","az1c", "","+","-","*","/","+1"]
		tokens = [stringToToken(x) for x in inputs]
		results = [0, 1, None, 0.0, 0.0, 45.0, None, None, None, None, None, None, None, None,"+","-","*","/",None]
		kinds = [num,num,err,num,num,num,err,err,cel,cel,err,err,err, err, op, op, op, op,err]
		#Verify it works on certain cases
		for t, r, k in zip(tokens,results, kinds):
			self.assertEqual(t.kind, k)
			if r is not None:
				self.assertEqual(t.value, r)
				#Verify cell values are correct!

	def test_index_bounds(self):
		""" Ensure we cannot go out of bounds """
		data = ["z1, 1",
				"c1, b1, k2, b2, c60"]
		result = "#ERR, 1.0" + os.linesep + "#ERR, 1.0, #ERR, 1.0, #ERR" + os.linesep
		output = io.StringIO()
		sheet = evalSheet(data)
		sheet.printResult(output)
		self.assertTrue(output.getvalue() == result)

	def test_recursion_limit(self):
		"""Ensure that exceeding max recursion does not break the program """
		data = []
		limit = sys.getrecursionlimit() + 5
		for i in range(limit):
			if i == limit - 1:
				data.append("1.5")
			else:
				cell = "a" + str(i + 1 + 1) # Add 1 because i starts at 0.
					# Second one is to look at next row
				data.append(cell)
		output = io.StringIO()
		sheet = evalSheet(data)
		sheet.printResult(output)
		res = output.getvalue().split()
		self.assertEqual(res[0], "#ERR")
		self.assertEqual(res[-1], "1.5")

	def test_loops(self):
		""" Ensure self-referential loops result in an error """
		data = [ ["a1"], ["b1, a1"], ["a2","a1"] ]
		result = ["#ERR" + os.linesep, "#ERR, #ERR" + os.linesep, "#ERR" + os.linesep + "#ERR" + os.linesep]
		sheets = [evalSheet(x) for x in data]
		for sheet, res in zip(sheets, result):
			output = io.StringIO()
			sheet.printResult(output)
			self.assertTrue(output.getvalue() == res)

	def test_evaluation(self):
		""" Test that normal recusrive evaluation works, including storing
			previously calculated values """
		data = ["e1, c1, e1, 2, f1, 7"]
		result = "7.0, 7.0, 7.0, 2.0, 7.0, 7.0" + os.linesep
		sheet = evalSheet(data)
		output = io.StringIO()
		sheet.printResult(output)
		self.assertEqual(output.getvalue(), result)

	def test_malformed(self):
		""" Test that malformed expressions result in #ERR """
		data = "1 o, 1 1 1 o, 1 1 1 1 o, o"
		result = "#ERR, #ERR, #ERR, #ERR" + os.linesep
		ops = ["+", "-", "*", "/"]
		for op in ops:
			sheet = evalSheet([data.replace("o", op)])
			output = io.StringIO()
			sheet.printResult(output)
			self.assertEqual(output.getvalue(), result)

	def test_expression(self):
		""" Test that basic expressions work as they should """
		data = ["1 2 +, 1 2 -, 1 2 *, 1 2 /"]
		result = "3.0, -1.0, 2.0, 0.5" + os.linesep
		sheet = evalSheet(data)
		output = io.StringIO()
		sheet.printResult(output)
		self.assertEqual(output.getvalue(), result)

	def test_symbolic_expression(self):
		""" Test that basic expressions work as they should """
		data = ["2, 1 a1 +, 1 a1 -, 1 a1 *, 1 a1 /"]
		result = "2.0, 3.0, -1.0, 2.0, 0.5" + os.linesep
		sheet = evalSheet(data)
		output = io.StringIO()
		sheet.printResult(output)
		self.assertEqual(output.getvalue(), result)

if __name__ == '__main__':
    unittest.main()
