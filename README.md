# Purpose
Association rules can aid in product placement/sales.

Association rules determine how likely a customer is to have a consequent
item in a cart given the antecedent is in the cart. In other words, if a
customer has milk in their cart, association rule can tell how likely
customer will put eggs in cart.

Lift values above 1 indicate increased chance of purchasing consequent item,
given antecedent purchased. The higher the value above 1, the higher the
chances.

Store managers should use association rules with high lift value for
placing of products. Eg: Manager creates combo deal, buy antecedent item,
get % off consequent item.


# Usage
The program reads all CSV files in `input` folder.
Format of all input CSV files should be `MemberNumber,Date,Item`.

Program will output data from model to `output` folder throughout course of
program. `3b_rule_stat.csv` is final output containing filtered association
rules. Repo already contains output results from default constraints.

Edit the `settings.json` to adjust constraints of `min_supp`, `min_conf`, 
`min_lift`. Go to [Verbose Details](#Verbose Details) section for 
explanation on support, confidence, lift.

# Structure
MVC pattern used.
Controller divided into:
1) PreController handling creation of transactions list from csv data
2) EclatController handling finding frequent itemsets from transactions
3) RuleController handling finding association rules from frequent itemsets

# Verbose Details
Support measures how frequent an itemset is in all transactions.
Association rules with low support should be ignored, since
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
whose confidence and lift are below the minimums will be filtered out and
not appear in `3b_rule_stat.csv` in `output` folder.