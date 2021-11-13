# Association Rule Mining
**November 2021**, cleaned up code and made public

**September-October 2020**, project completion date

This Python program processes grocery store data provided in a CSV file. Then, it generates association rules using the ECLAT (Equivalence Class Clustering and Bottom-Up Lattice Traversal) algorithm. No packages were used to implement the ECLAT algorithm itself, it was made from scratch. The program writes association rules and other data into new CSV files.

Association rule info can be used to increase profits at a grocery store. Association rules with high lift values (greater than 1) means that if a customer buys the antecedent item, the customer is likely going to buy the consequent as well. Store managers can use this info for product placement.

## Example

The `example-results` folder contains results of running program with minimum support of 15, minimum confidence of .10, and minimum lift of 1.05. Terminal output is below:
```
Enter MIN_SUPPORT(integer): 15
Enter MIN_CONFIDENCE(double): .10
Enter MIN_LIFT(double): 1.05
NUM_TRANSACTIONS=14963
HIGHEST_NUM_ITEMS_IN_TRANS=10
prunedDictSize= 601
Time elasped for eclat=0.55s
Time elasped for entire program=0.89s
End of program.
```
Below is portion of association rule data that is stored in CSV file in this example.

| Size | Antecedent                | Consequent   | Support(A->C) | Confidence(A->C) | Lift(A->C) |
|:----:|---------------------------|--------------|---------------|------------------|------------|
| 3    | ('whole milk', 'yogurt')  | ('sausage',) | 0.00147       | 0.1317           | 2.1825     |
| 3    | ('sausage', 'whole milk') | ('yogurt',)  | 0.00147       | 0.1642           | 1.9118     |
