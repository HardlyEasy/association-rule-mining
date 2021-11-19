# Association Rule Mining
**November 2021**, cleaned up code and made public

**September-October 2020**, project completion date

## Program description

This Python program contains an implementation of the ECLAT 
(Equivalence Class Clustering and Bottom-Up Lattice Traversal) algorithm and 
helper functions to process CSV data read from a CSV file.
Frequent itemsets are mined using the ECLAT algorithm.
The ECLAT algorithm is considered done once frequent itemsets are generated.
Once ECLAT is finished, using the frequent itemsets, we can generate 
association rules.

## Rule generation

The ECLAT algorithm does not give confidence or lift values. Another step needs
to be done after to generate association rules from frequent itemsets. These 
rules can be used to increase profits at a grocery store. Association rules
with high lift values (greater than 1) means that if a customer buys the 
antecedent item, the customer is likely to buy the consequent as well. This
is helpful for product placement at stores.


## Example

The `example-results` folder contains results of running program with minimum 
support of 15, minimum confidence of .10, and minimum lift of 1.05. 

Terminal output is below:
```
Fill me in later
```
Below is portion of association rule data that is stored in CSV file in this example.

| Size | Antecedent                | Consequent   | Support(A->C) | Confidence(A->C) | Lift(A->C) |
|:----:|---------------------------|--------------|---------------|------------------|------------|
|     |   |  |        |            |      |
|     |  |   |        |            |      |
