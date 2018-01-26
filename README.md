Joshua Kelly
inst.zombie@gmail.com
(303) 974-8156

To invoke the program, run (using python 3):

python spreadsheet_working.py

For input, it looks for a file called input1.csv.  I chose this over
command line arguments due to simplicity of implementation.

The program will write output.csv upon completion.

A sample file (from the assignment) could be:

>
>b1 b2 +,2 b2 3 * -,3,+
>a1 ,5, ,7 2 /
>c2 3 * ,1 2 , ,5 1 2 + 4 * + 3 -

Unlike the assignment, I inserted a blank line.  Blank lines evaluate to 
a single cell with value 0.

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