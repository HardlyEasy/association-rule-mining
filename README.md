# Association Rule Mining
Association rule mining is divided into two steps:

1) Itemset generation (there are various algorithms for this)
2) Rule generation

# Program Guide
This Python program contains an implementation of the ECLAT
(Equivalence Class Clustering and Bottom-Up Lattice Traversal) algorithm for
frequent itemset generation. Then, it generates rules from these frequent
itemsets.

## Project structure
`dev` folder contains verbose output at various steps of program running

`results` folder contains association rules, filtered by minimum confidence
and minimum lift

## Support, confidence, lift
Keep the information below in mind when prompted for min support,
min confidence(A->C), and min lift(A->C).

Support measures how frequent an itemset is in all transactions.
Association rules with low support should be ignored, since there
it does not occur frequently enough to draw any conclusions from.

Confidence measures likelihood of occurrence of consequent being on shopping
cart given that customer already has antecedent on shopping cart.

Lift is greater than 1 in cases where antecedent leads to consequent.
The higher the value of lift above 1, the greater chances that customer
will buy consequent if they have already bought antecedent.
Lift is the most important for product placement.

## Example
`dev` and `results` folder have output when running program with minimum
support of 15, minimum confidence of .10, and minimum lift of 1.00.

Terminal output is below:
```
Enter minimum support (int): 15
Enter minimum confidence(A->C) (float): .10
Enter minimum lift(A->C) (float): 1.00
0.65  seconds total runtime
End of program.
```
Below is portion of association rule data in csv file in `results` folder:

|Antecedent|Consequent|Support(A->C)|Confidence(A->C)|Lift(A->C) |
|:----:|----|----|----|----|
|('flour',)|('tropical fruit',)|0.0011|0.1096|1.6171|
|('whole milk', 'yogurt')|('sausage',)|0.0015|0.1317|2.1829

# Developer section

## Psuedocode
Data processing (creating transactions list from csv file for ECLAT steps)

1) Read CSV file and store csv row data in a list
   1) eg `[['1702', '12-01-2014', 'pip fruit'], ...]`
2) Make verbose transactions list (verbose meaning it includes member number
   , date, number of items), this merges csv row data with same member
   number and date
   1) eg `[['1702','12-01-2014','3','pip fruit','yogurt','yogurt'], ... ]`
3) Filter duplicate items from verbose transactions list
   1) eg `[['1702','12-01-2014','2','pip fruit','yogurt'], ... ]`
4) Make transactions list by removing member number, date, and num items data
   1) eg `[['pip fruit','yogurt'], ... ]`

ECLAT algorithm

A tid (transaction id) is the index of transactions list where you can
find item or itemset

5) Create item tidset dictionary using transactions list (Step 4)
   2) eg `{'pip fruit': {10240, 10242, ...}, ... }`
6) Create itemset tidset dictionary, keys of all k-itemset combinations
   possible at each transaction, entries must be above minimum support
   1) eg `{('pastry',): {0, ...}, ...,
      ('whole milk', 'frozen meals'): {4100, ...}, ...}`
   2) Loop, start with k=1, acting on k-itemset tidset dictionary,
      1-itemset is initialized from (Step 5)
      1) Filter entries below minimum support
         1) If we no entries remain, break out of loop
      2) Create itemset combinations of k size
      3) Find tidset for each itemset combinations with set intersection, use
         item tidset dictionary (Step 4) for fast lookups
      4) k++
      
Rule generation

7) Create itemset rule dictionary
   1) eg `{itemset_tuple: [(antecedent_set, consequent_set), ...] }`
   2) eg `{('ham', 'whole milk'):
      [({'ham'}, {'whole milk'}), ({'whole milk'}, {'ham'}), ...] }`
8) Create rule statistics dictionary
   1) eg `{(antecedent_tuple, consequent_tuple):
      (support, confidence, lift), ...}`
   2) eg `{(('frankfurter',), ('other vegetables',)):
      (0.0051, 0.1363, 1.1163), ...}`
9) Write association rule and statistics (Step 8) neatly into a CSV file
in results folder