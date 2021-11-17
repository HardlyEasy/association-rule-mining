import csv
import operator
from datetime import datetime
from itertools import combinations
from itertools import permutations

CSV_FILENAME = 'grocery_data.csv'  # place csv in same directory as py file
RESULT_FOLDER = 'results'  # place folder in same directory as py file


def promptUser():
    """ Prompts user for minimum support, minimum confidence and minimum lift
    This will affect association rule generation

    :return: Tuple with minimum support, minimum confidence, minimum lift
    :rtype: (int, float, float)
    """
    min_support = int(input("Enter minimum support (int): "))
    min_confidence = float(input('Enter minimum confidence (float): '))
    min_lift = float(input('Enter minimum lift (float): '))
    return min_support, min_confidence, min_lift


def read_csv(csv_filename):
    """ Reads a csv file and returns csv data list ,csv data list elements are
    lists representing data in each row

    :param csv_filename: eg 'filename.csv'
    :type csv_filename: str
    :return: A list with each element being another list with row data in it
        eg [ [row1col1, row1col2, ...], [row2col1, row2col2, ...], ... ]
    :rtype: list
    """
    csv_data = []
    with open(csv_filename, mode='r', encoding='latin1') as csvfile:
        csv_reader = csv.reader(csvfile, dialect='excel', delimiter=',',
                                quoting=csv.QUOTE_ALL)
        for row in csv_reader:
            csv_data.append(row)
    return csv_data


def sort_csv_data(csv_data):
    """ Sorts csv data in priority of member id, then date, then item name

    :param csv_data: A list of lists with customer number, date, and item name
        eg [ ['1808', '21-07-2015', 'tropical fruit'],
        ['2552', '05-01-2015', 'whole milk'], ... ]
    :type csv_data: list
    :return: A list of the same csv data, but now sorted by grocery item,
        then date, then member number
    :rtype: list
    """
    # Sort by grocery item
    temp1 = sorted(csv_data, key=operator.itemgetter(2))
    # Sort by date
    temp2 = sorted(temp1, key=lambda d: datetime.strptime(d[1], "%d-%m-%Y"))
    # Sort by member number
    sorted_csv_data = sorted(temp2, key=operator.itemgetter(0))
    return sorted_csv_data


def write_csv(filename, data, header=None):
    """ Writes data in a list or dict to a csv file on computer

    :param filename: eg "output_file_name.csv"
    :type filename: str
    :param data: List of lists, where each inner list represents a row
        Dictionary, where keys go on column1 and values go on column2
    :type data: list or dict
    :param header: The first row
    :type header: list, optional
    :param data: Either a list or dict
        eg [ ['1808,21-07-2015', 'tropical fruit'],
        ['2552', '05-01-2015', 'whole milk'], ... ]
        eg { 'rubbing alcohol': {5348, 13062, 14833, 7443, 6739},
        ('detergent', 'pork'): {196, 14397, 4486}, ... }
    :type data: list or dict
    """
    with open(filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        if header is not None:
            csv_writer.writerow(header)
        if type(data) == list:
            csv_writer.writerows(data)
        if type(data) == dict:
            for i in data.items():
                csv_writer.writerow(i)


def create_transactions(csv_data):
    """ Creates and returns a transaction list, which contains transactions
    A transaction is [memberNumber,date,numItems,item1,item2,...] it is all
    the items a member has bought on a specific date. Transactions can contain
    duplicate items, for example ['1698','17-01-2014','2','yogurt','yogurt']

    :param csv_data:
    :type csv_data: list
    :return: List containing transaction data
        eg [ ['1702','12-01-2014','3','pip fruit','yogurt,'yogurt'], ... ]
        where format is [ [memberNumber,date,numItems,item1,item2,...], ... ]
    :rtype: list
    """
    transaction_list = []
    transaction = csv_data[0]  # first transaction to add csv items to
    for i in range(1, len(csv_data)):
        csv_number = csv_data[i][0]  # member number
        csv_date = csv_data[i][1]
        csv_item = csv_data[i][2]
        trans_number = transaction[0]
        trans_date = transaction[1]
        # member id or date are different, so we add our built up transaction
        # to transaction_list and create a new transaction that we can
        # add csv_items onto
        if (trans_number != csv_number) or (trans_date != csv_date):
            num_items = len(transaction) - 2
            transaction.insert(2, str(num_items))
            transaction_list.append(transaction)
            transaction = [csv_number, csv_date, csv_item]
        # member id and date are same, so add csv_item onto transaction
        else:
            transaction.append(csv_item)
    num_items = len(transaction) - 2
    transaction.insert(2, str(num_items))
    transaction_list.append(transaction)
    return transaction_list


def remove_duplicates(transactions):
    """ Takes a transactions list and removes all duplicate grocery items in
    all transaction elements

    :param transactions: List containing transaction data, with duplicates
        eg [ ['1702','12-01-2014','3','pip fruit','yogurt','yogurt'], ... ]
    :type transactions: list
    :return: Same as input param, except duplicate grocery items removed,
        which makes the grocery items into an itemset (because no duplicates)
        eg [ ['1702','12-01-2014','2','pip fruit','yogurt'], ... ]
    :rtype: list
    """
    transactions_no_duplicates = []
    for t in transactions:
        item_set = list(set(t[3:]))  # remove duplicates
        item_set = sorted(
            item_set)  # sort again (becomes unordered for some reason)
        new_transaction = t[:3]
        new_transaction.extend(item_set)
        # set num items in item_set
        new_transaction[2] = len(new_transaction) - 3
        transactions_no_duplicates.append(new_transaction)
    return transactions_no_duplicates


def get_itemsets(transactions):
    """ Returns list with only grocery item sets from transactions list

    :param transactions: List containing transactions
        eg [ ['1702','12-01-2014','3','pip fruit','yogurt,'yogurt'], ... ]
    :type transactions: list
    :return: List containing item sets
        eg [ ['pip fruit','yogurt,'yogurt'], ... ]
    :rtype: list
    """
    item_sets = []
    for t in transactions:
        item_sets.append(t[3:])
    return item_sets


def create_dict(item_sets, max_items_item_set):
    """ Creates a dictionary with keys being all combinations of item sets
    and values being transaction ids aka t-ids (equivalent to index of
    item_sets list)

    :param item_sets: List of item sets (no duplicate items)
        eg [ ['pastry','salty snack','whole milk'], ... ]
    :type item_sets: list
    :param max_items_item_set: The max number of items in a item set
    :type max_items_item_set: int
    :return: A dict mapping keys of all combinations of possible item
        sets to values of t-ids where you can find said value
        eg item set at index 94 has
        [fish,other vegetables,root vegetables,tropical fruit]
        dict has
        {..., ('fish','other vegetables'): {12296, 6883, 94, 12550},
        ('fish', 'root vegetables): {4363, 94, 12975}, ...}
    :rtype: dict
    """
    item_sets_dict = dict()
    # 1-itemset
    for tid in range(0, len(item_sets)):
        an_item_set = item_sets[
            tid]  # eg ['pastry','salty snack','whole milk']
        for i in range(0, len(an_item_set)):
            item = an_item_set[i]
            if item not in item_sets_dict:
                item_sets_dict[item] = {tid}
            else:  # add onto existing key
                item_sets_dict[item].add(tid)
    # k-itemset, k>1
    for k in range(2, max_items_item_set + 1):
        for tid in range(0, len(item_sets)):
            # combination puts values in lexigraphic order
            # thus indexes may not be in numeric order
            comb = combinations(item_sets[tid], k)
            comb_list = list(comb)
            for k_item_set in comb_list:
                if k_item_set not in item_sets_dict:
                    item_sets_dict[k_item_set] = {tid}
                else:  # add onto existing key
                    item_sets_dict[k_item_set].add(tid)
    return item_sets_dict


def create_k_items(item_sets_dict):
    """ Returns a list containing lists with k, k-item set, and number of
    occurrences of k-item set

    :param item_sets_dict: Item set to tid dictionary
        eg { 'rubbing alcohol': {5348, 13062, 14833, 7443, 6739},
        ('detergent', 'pork'): {196, 14397, 4486}, ... }
    :type item_sets_dict: dict
    :return: A list of lists
        eg [ [1, 'whole milk', 2363], ..., [2, ('oil', 'yogurt'), 16], ...]
    :rtype: list
    """
    k_items = []
    for key, value in item_sets_dict.items():
        temp_list = []
        if type(key) is tuple:
            temp_list.append(len(key))  # k
        else:
            temp_list.append(1)
        temp_list.append(key)  # k-item set
        temp_list.append(len(value))  # number of occurrences
        k_items.append(temp_list)
    # Sort by number of occurrences
    k_items = sorted(k_items, key=operator.itemgetter(2), reverse=True)
    # Sort by k
    k_items = sorted(k_items, key=operator.itemgetter(0), reverse=False)
    return k_items


def prune_dict(item_sets_dict, min_support):
    """ Removes all k-item sets with k equal to 1 and with number of
    occurrences of item set less than or equal to minimum support

    :param item_sets_dict:
    :type item_sets_dict: dict
    :param min_support:
    :type min_support: int
    :return:
    :rtype: dict
    """
    pruned_item_sets_dict = dict()
    for key, value in item_sets_dict.items():
        if (type(key) is tuple) & (len(value) >= min_support):
            pruned_item_sets_dict[key] = value
    return pruned_item_sets_dict


# =====================================
# Generate itemset to association rules dict
#     key = itemset tuple
#     value = list of tuples, each tuple being association rule of form (A,C)
# =====================================
def generateItemsetAssocDict(kitemset_assoc_dict, item_set_tid_dict):
    assoc_rule_lst = []
    for key, value in itemset_tid_dict.items():
        itemset = key
        for i in range(1, len(itemset)):
            comb = combinations(itemset, i)
            list_combo = list(comb)
            for j in range(0, len(list_combo)):
                antecedent = list_combo[j]  # tuple
                consequent = set(itemset) - set(list_combo[j])
                consequent = tuple(consequent)
                temp_tuple = (antecedent, consequent)
                assoc_rule_lst.append(temp_tuple)
        kitemset_assoc_dict[itemset] = assoc_rule_lst
        assoc_rule_lst = []
    return kitemset_assoc_dict


# =====================================
# Generate association rule to statistics dictionary
#   key = tuple of form (A,C)
#   value = tuple of form (support(A->C),confidence(A->C),lift(A->C))
# =====================================
def generateAssocStatDict(itemset_tid_dict, kitemset_assoc_dict):
    assoc_stat_dict = dict()
    for key, value in kitemset_assoc_dict.items():
        support_a_c = len(itemset_tid_dict[key]) / num_transactions
        for i in range(0, len(value)):
            assoc_rule = value[i]
            antecedent = assoc_rule[0]
            consequent = assoc_rule[1]
            if (len(antecedent) == 1):
                antecedent = antecedent[0]  # turn single tuple into just item
            if (len(consequent) == 1):
                consequent = consequent[0]  # turn single tuple into just item
            # rearrange antecedent until it gets a match in itemset_tid_dict
            if (antecedent not in itemset_tid_dict):
                perm = permutations(antecedent, len(antecedent))
                list_perm = list(perm)
                for p in list_perm:
                    if (p in itemset_tid_dict):
                        support_a = len(itemset_tid_dict[p]) / num_transactions
                        break
            else:
                support_a = len(
                    itemset_tid_dict[antecedent]) / num_transactions
            # rearrange consequent until it gets a match in itemset_tid_dict
            if (consequent not in itemset_tid_dict):
                perm = permutations(consequent, len(consequent))
                list_perm = list(perm)
                for p in list_perm:
                    if (p in itemset_tid_dict):
                        support_c = len(itemset_tid_dict[p]) / num_transactions
                        break
            else:
                support_c = len(
                    itemset_tid_dict[consequent]) / num_transactions
            confidence_a_c = support_a_c / support_a
            lift_a_c = confidence_a_c / support_c
            # prune out rules below mins
            if ((confidence_a_c < min_confidence) | (lift_a_c < min_lift)):
                continue
            # round off
            support_a_c = round(support_a_c, 4)
            confidence_a_c = round(confidence_a_c, 4)
            lift_a_c = round(lift_a_c, 4)
            assoc_stat_dict[assoc_rule] = [support_a_c, confidence_a_c,
                                           lift_a_c]
    return assoc_stat_dict


def writeAssocStatDictToCsv(output_fname, assoc_stat_dict):
    first_row = ['Itemset Size', 'Antecedent', 'Consequent',
                 'support(A->C)', 'confidence(A->C)', 'lift(A->C)']
    csv_lst = []
    for key, value in assoc_stat_dict.items():
        temp_lst = []
        temp_lst.append(len(key[0]) + len(key[1]))
        temp_lst.append(key[0])  # antecedent
        temp_lst.append(key[1])  # consequent
        temp_lst.append(value[0])  # support(A->C)
        temp_lst.append(value[1])  # confidence(A->C)
        temp_lst.append(value[2])  # lift (A->C)
        csv_lst.append(temp_lst)
    # Sort by confidence
    csv_lst = sorted(csv_lst, key=operator.itemgetter(4), reverse=True)
    # Sort itemset size
    csv_lst = sorted(csv_lst, key=operator.itemgetter(0), reverse=True)
    with open(output_fname, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(first_row)
        for row in csv_lst:
            csvwriter.writerow(row)





def main():
    min_support, min_confidence, min_lift = (15, .10, 1.05)

    # Read CSV file data into a list and sort that list
    csv_data = read_csv(CSV_FILENAME)
    csv_data = csv_data[1:]  # remove field name row
    sorted_csv_data = sort_csv_data(csv_data)

    """ transactions contains transaction data, each transaction having
    member number, date, number of items purchased, and item names, there can
    be duplicate item names
    eg [ ['1702','12-01-2014','3','pip fruit','yogurt,'yogurt'], ... ]
    """
    transactions_items = create_transactions(sorted_csv_data)
    write_csv("results/transactions_items.csv", transactions_items,
              ['Member number', 'Date', 'Number of items'])

    """ transactions_no_duplicates is same as transactions, but instead of 
    items it now has item sets because we remove any duplicate items
    eg [ ['1702','12-01-2014','2','pip fruit','yogurt'], ... ]
    """
    transactions_item_sets = remove_duplicates(transactions_items)
    write_csv(RESULT_FOLDER + "/transactions_item_sets.csv",
              transactions_item_sets, ['Member number', 'Date',
                                       'Number of items'])

    """ item_sets is a stripped version of transactions_no_duplicates list, it 
    contains only grocery item data
    eg [ ['pip fruit','yogurt,'yogurt'], ... ]
    """
    item_sets = get_itemsets(transactions_item_sets)
    write_csv(RESULT_FOLDER + "/item_sets.csv", item_sets)

    """ item_sets_dict maps item_sets to transaction ids (t-ids), t-ids 
    being equivalent to index numbers of item_sets list
    eg { 'rubbing alcohol': {5348, 13062, 14833, 7443, 6739},
        ('detergent', 'pork'): {196, 14397, 4486}, ... }
    """
    item_sets_dict = create_dict(item_sets, 10)
    write_csv(RESULT_FOLDER + "/item_sets_dict.csv", item_sets_dict)

    """ k_item_sets contains data on number of occurrences of each k-itemset
    combination
    eg [ [1, 'whole milk', 2363], ... , 
    [2, ('rice', 'rolls/buns'), 5], ... ]
    """
    k_item_sets = create_k_items(item_sets_dict)
    write_csv(RESULT_FOLDER + "/k_item_sets.csv", k_item_sets,
              ['k', 'k-item set', 'Number of occurrences'])

    """ item_sets_dict_pruned removes dict entries that have 1-item set
    or have item set occurrences below the minimum support value, this should
    significantly reduce the size of the dictionary
    """
    item_sets_dict_pruned = prune_dict(item_sets_dict, min_support)
    write_csv(RESULT_FOLDER + "/item_sets_dict_pruned.csv", item_sets_dict_pruned,
              ['k', 'k-item set', 'Number of occurrences'])


    """
    kitemset_assoc_dict = generateItemsetAssocDict(dict(),
                                                   pruned_itemset_tid_dict)

    print(kitemset_assoc_dict)

    
    # =====================================================
    # Generate association rules and store as CSV
    # =====================================================
    assoc_stat_dict = generateAssocStatDict(itemset_tid_dict,
                                            kitemset_assoc_dict)
    writeAssocStatDictToCsv('Association_Rules.csv', assoc_stat_dict)

    print("End of program.")
    """


if __name__ == "__main__":
    main()
