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
