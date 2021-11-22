# Association Rule Mining
Association rule mining is divided into two steps:

1) Itemset generation (there are various algos for this)
2) Rule generation

Association rules can be used to determine how likely a customer is 
to have a consequent item in a cart given that the antecedent is in the cart.
So, in simpler terms, if a customer has milk in their cart, then an
association rule could tell us how likely a customer will put eggs in their
shopping cart. For this reason, association rule mining is often done on 
shopping data so that store managers can create better product 
placement and deals.

# Program Guide
This Python program contains an implementation of the ECLAT
(Equivalence Class Clustering and Bottom-Up Lattice Traversal) algorithm for
frequent itemset generation. Once ECLAT has finished, the program will 
generate association rules using the frequent itemsets. A transactions
list for use by ECLAT is created from a grocery store data CSV file.

## Project structure

`CSV_FILENAME`, `RESULT_FOLDER`, `DEV_FOLDER` are global variables

`DEV_FOLDER` is where verbose output at various parts of program is written

`RESULT_FOLDER` contains association rules generated

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

Minimum support will affect ECLAT algorithm's frequent itemset generation.
Itemsets whose frequency of occurrence in transactions is below minimum support
will be filtered out. A lower support will lead to higher ECLAT runtime
since less filtering will be done.

Minimum confidence and lift will affect the filtering of rules that were
generated in the Rule Generation part of the program. Association rules 
whose confidence and lift are below the minimums will be filtered out 
when we print out the results in `results` folder.

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
|('flour',)|('tropical fruit',)|0.001069|0.1096|1.6171|
|('whole milk', 'yogurt')|('sausage',)|0.00147|0.1317|2.1829

# Developer section

## Psuedocode

Data processing

1) Create transactions list 
   1) Filters csv data so items bought by same member number and
      date are all grouped 
   2) eg `[ ['pip fruit','yogurt'], ... ]`

ECLAT algorithm

2) Make item to tidset dictionary 
   1) A tid (transaction id) is the index of transactions list where you can
      find item/itemset
   2) eg `{ 'pastry': {0, 4096, ... }, ... }`

3) Create frequent itemset to tidset dictionary
   1) eg `{ ('pastry',): 
   {0, 4096, ...}, ('pastry', 'pork'): {11395, 5131, ...}, ... }`

Statistics for graphs/reports (not part of ECLAT or rule generation)

4) Make list with k, k-itemset, and number of occurrences
   1) eg `[ [1, ('whole milk',), 2363], ..., 
   [2, ('rice', 'rolls/buns'), 5], ... ]`

Rule generation

5) Make dictionary with frequent itemset to list of association rules 
   1) eg `('soda', 'whole milk', 'rolls/buns'):
      [ ({'soda'}, {'rolls/buns', 'whole milk'}), ...
      ({'soda', 'whole milk'}, {'rolls/buns'}), ... ]`

6) Make dictionary with association rule to statistics (supp, conf, lift)
   1) eg `{ (('frankfurter',), ('other vegetables',)):
      (0.0051, 0.1363, 1.1163), ... }`

7) Make sorted/pretty list with association rules, statistics
   1) format `['Size(A+C)', 'Size(A)', 'Antecedent',
      'Size(C)', 'Consequent',
      'Support(A->C)', 'Confidence(A->C)', 'Lift(A->C)']`
   2) eg `[ [2, 1, ('citrus fruit',), 1, ('sausage',),
      0.001203, 0.0226, 0.3752], ...]`

8) Write pretty list to CSV file in results folder