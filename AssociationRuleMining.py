import csv
import operator
import os
import time
from datetime import datetime
from itertools import combinations
from itertools import permutations


CSV_FILENAME = 'grocery_data.csv'  # place csv in same directory as py file
RESULT_FOLDER = 'results'  # place folder in same directory as py file
DEV_FOLDER = 'dev'
DEV_MODE = True  # toggle writing of csv data at each step of eclat


def promptUser():
    """ Prompts user for minimum support, minimum confidence and minimum lift
    This will affect association rule generation

    :return: Tuple with minimum support, minimum confidence, minimum lift
    :rtype: (int, float, float)
    """
    min_support = int(input('Enter minimum support (int): '))
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


def write_csv(folder_path, filename, data, header=None):
    """ Writes data in a list or dict to a csv file on computer

    :param folder_path: Full path to where you want csv file written
    :type folder_path: str
    :param filename: Filename of csv file you want written
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
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    write_path = os.path.join(folder_path, filename)
    with open(write_path, 'w', newline='') as csv_file:
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
        itemset = list(set(t[3:]))  # remove duplicates
        # sort again (becomes unordered for some reason)
        itemset = sorted(itemset)
        new_transaction = t[:3]
        new_transaction.extend(itemset)
        # set num items in itemset
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
    itemsets = []
    for t in transactions:
        itemsets.append(t[3:])
    return itemsets


def find_max_itemset(itemsets):
    """ Find max number of items in an itemset

    :param itemsets: List of itemsets
    :type itemsets: list
    :return: Max number of items in an itemset
    :rtype: int
    """
    max_itemset = 0
    for an_itemset in itemsets:
        if len(an_itemset) > max_itemset:
            max_itemset = len(an_itemset)
    return max_itemset


# TODO: Fix single items being present in return dict
def create_itemset_tid_dict(itemsets, max_items, min_support):
    """

    """
    # Make dictionary of key of single item to value of set of tids
    item_tid_dict = dict()
    for tid in range(0, len(itemsets)):
        an_itemset = itemsets[tid]  # eg ['pastry','salty snack','whole milk']
        for i in range(0, len(an_itemset)):
            item = an_itemset[i]
            if item not in item_tid_dict:
                item_tid_dict[item] = {tid}
            else:  # add onto existing key
                item_tid_dict[item].add(tid)
    # Filter out results that are below minimum support


    full_itemset_tid_dict = dict()  # The return dictionary

    k = 1
    k_itemset_tid_dict = item_tid_dict.copy()  # aka kitemset dict
    full_itemset_tid_dict = dict()
    # TODO: this is related to why single items are repeated in dict
    full_itemset_tid_dict.update(k_itemset_tid_dict)
    while True:  # Loop until no more itemset-tidset pairs can be combined
        # 1) Filter
        k_itemset_tid_dict = dict(
            filter(
                lambda entry: len(entry[1]) >= min_support,
                k_itemset_tid_dict.items()
            )
        )
        print(k,'filtered_dict_len=',len(k_itemset_tid_dict))
        # 2) Create all itemset combinations
        if k == 1:
            items_list = list(k_itemset_tid_dict.keys())
        else:
            items_list = set()
            for itemset in k_itemset_tid_dict.keys():
                for item in itemset:
                    items_list.add(item)
            items_list = list(items_list)

        comb_start_time = time.time()
        combs = list(combinations(items_list, k))
        #print(combs[0])
        comb_end_time = time.time()
        print('comb_time=', round(comb_end_time-comb_start_time,2), 'seconds')
        next_k_itemset_tid_dict = dict()
        # 3)
        for a_comb in combs:
            item0 = a_comb[0]  # first combination
            # initialize tidset with first tidset
            tidsets_intersect = item_tid_dict[item0]
            for i in range(1, len(a_comb)):
                next_item = a_comb[i]
                next_tidset = item_tid_dict[next_item]
                tidsets_intersect = tidsets_intersect.intersection(next_tidset)
            if len(tidsets_intersect) >= min_support:
                next_k_itemset_tid_dict[a_comb] = tidsets_intersect

        # No combinations above minimum support were generated
        if len(next_k_itemset_tid_dict) == 0:
            break
        full_itemset_tid_dict.update(next_k_itemset_tid_dict)
        k_itemset_tid_dict = next_k_itemset_tid_dict.copy()
        k += 1
    return full_itemset_tid_dict

# TODO: helpful possibly but not needed for eclat
def create_k_itemsets(itemset_tid_dict):
    """ Returns a list containing lists with k, k-item set, and number of
    occurrences of k-item set

    :param itemset_tid_dict: Item set to tid dictionary
        eg { 'rubbing alcohol': {5348, 13062, 14833, 7443, 6739},
        ('detergent', 'pork'): {196, 14397, 4486}, ... }
    :type itemset_tid_dict: dict
    :return: A list of lists
        eg [ [1, 'whole milk', 2363], ..., [2, ('oil', 'yogurt'), 16], ...]
    :rtype: list
    """
    k_itemsets = []
    for key, value in itemset_tid_dict.items():
        temp_list = []
        if type(key) is tuple:
            temp_list.append(len(key))  # k
        else:
            temp_list.append(1)
        temp_list.append(key)  # k-item set
        temp_list.append(len(value))  # number of occurrences
        k_itemsets.append(temp_list)
    # Sort by number of occurrences
    k_itemsets = sorted(k_itemsets, key=operator.itemgetter(2), reverse=True)
    # Sort by k
    k_itemsets = sorted(k_itemsets, key=operator.itemgetter(0), reverse=False)
    return k_itemsets


# TODO: this is redundant now
def prune_itemset_tid_dict(itemset_tid_dict, min_support):
    """ Removes all k-item sets with k equal to 1 and with number of
    occurrences of item set less than or equal to minimum support

    :param itemset_tid_dict: Maps combinations of itemsets to tids
    :type itemset_tid_dict: dict
    :param min_support:
    :type min_support: int
    :return: Same as input dictionary, but with pruned elements
    :rtype: dict
    """
    itemsets_tid_dict_pruned = dict()
    for key, value in itemset_tid_dict.items():
        #  if (type(key) is tuple) & (len(value) >= min_support):
        if len(value) >= min_support:
            itemsets_tid_dict_pruned[key] = value

    return itemsets_tid_dict_pruned


# Generate itemset to association rules dict
#     key = itemset tuple
#     value = list of tuples, each tuple being association rule of form (A,C)
def create_itemset_rule_dict(itemset_rule_dict, itemset_tid_dict):
    assoc_rule_lst = []
    for key,value in itemset_tid_dict.items():
        itemset = key
        for i in range (1, len(itemset)):
            comb = combinations(itemset,i)
            list_combo = list(comb)
            for j in range(0, len(list_combo)):
                antecedent = list_combo[j] # tuple
                consequent = set(itemset) - set(list_combo[j])
                consequent = tuple(consequent)
                temp_tuple = (antecedent,consequent)
                assoc_rule_lst.append(temp_tuple)
        itemset_rule_dict[itemset] =  assoc_rule_lst
        assoc_rule_lst = []
    return itemset_rule_dict


# Generate association rule to statistics dictionary
#   key = tuple of form (A,C)
#   value = tuple of form (support(A->C),confidence(A->C),lift(A->C))
def create_rule_stat_dict(itemset_tid_dict, itemset_rule_dict, constraints,
                          num_transactions):
    min_support = constraints[0]
    min_confidence = constraints[1]
    min_lift = constraints[2]
    rule_stat_dict = dict()
    for key,value in itemset_rule_dict.items():
        support_a_c = len(itemset_tid_dict[key])/num_transactions
        for i in range(0, len(value)):
            assoc_rule = value[i]
            antecedent = assoc_rule[0]
            consequent = assoc_rule[1]
            if (len(antecedent) == 1):
                antecedent = antecedent[0] # turn single tuple into just item
            if (len(consequent) == 1):
                consequent = consequent[0] # turn single tuple into just item
            # rearrange antecedent until it gets a match in itemset_tid_dict
            if(antecedent not in itemset_tid_dict):
                perm = permutations(antecedent,len(antecedent))
                list_perm = list(perm)
                for p in list_perm:
                    if(p in itemset_tid_dict):
                        support_a = len(itemset_tid_dict[p]) / num_transactions
                        break
            else:
                support_a = len(itemset_tid_dict[antecedent]) / num_transactions
            # rearrange consequent until it gets a match in itemset_tid_dict
            if(consequent not in itemset_tid_dict):
                perm = permutations(consequent,len(consequent))
                list_perm = list(perm)
                for p in list_perm:
                    if(p in itemset_tid_dict):
                        support_c = len(itemset_tid_dict[p]) / num_transactions
                        break
            else:
                support_c = len(itemset_tid_dict[consequent]) / num_transactions
            confidence_a_c = support_a_c/support_a
            lift_a_c = confidence_a_c/support_c
            # prune out rules below mins
            if ( (confidence_a_c < min_confidence ) | (lift_a_c < min_lift)):
                continue
            # round off
            support_a_c = round(support_a_c,4)
            confidence_a_c = round(confidence_a_c,4)
            lift_a_c = round(lift_a_c, 4)
            rule_stat_dict[assoc_rule] = [support_a_c,confidence_a_c,lift_a_c]
    return rule_stat_dict



def write_rule_stat_dict(filename, rule_stat_dict):
    first_row = ['Itemset Size', 'Antecedent', 'Consequent',
                 'support(A->C)', 'confidence(A->C)', 'lift(A->C)']
    csv_lst = []
    for key, value in rule_stat_dict.items():
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
    with open(filename, 'w',  newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(first_row)
        for row in csv_lst:
            csv_writer.writerow(row)


def main():
    start_time = time.time()
    min_support, min_confidence, min_lift = (15, .10, 1.05)
    constraints = (min_support, min_confidence, min_lift)
    folder_path = os.path.join(os.getcwd(), DEV_FOLDER)

    """ Read CSV file data into a list and sort that list
    a csv row should look like: 1808,21-07-2015,tropical fruit
    There will be only one item per row
    """
    csv_data = read_csv(CSV_FILENAME)
    csv_data = csv_data[1:]  # remove field name row
    sorted_csv_data = sort_csv_data(csv_data)

    """ Store transaction data gathered from csv file
    eg [ ['1702','12-01-2014','3','pip fruit','yogurt,'yogurt'], ... ]
    where each transaction is [member_number, date, num_items, item_name1, ...]
    """
    transactions_items = create_transactions(sorted_csv_data)
    write_csv(folder_path, 'transactions_items.csv', transactions_items,
              ['Member number', 'Date', 'Number of items'])


    """ Remove all duplicate items so items in each transaction can now be
    considered an item set
    eg [ ['1702','12-01-2014','2','pip fruit','yogurt'], ... ]
    """
    transactions_itemsets = remove_duplicates(transactions_items)
    write_csv(folder_path, 'transactions_itemsets.csv',
              transactions_itemsets, ['Member number', 'Date',
                                      'Number of items'])

    """ Get only item set data from transactions
    eg [ ['pip fruit','yogurt,'yogurt'], ... ]
    """
    itemsets = get_itemsets(transactions_itemsets)
    write_csv(folder_path, 'itemsets.csv', itemsets)

    """ Map all combinations of item sets to transaction id (tid) sets
    tids match the indexes where you can find item set in itemsets list
    eg { 'rubbing alcohol': {5348, 13062, 14833, 7443, 6739},
        ('detergent', 'pork'): {196, 14397, 4486}, ... }
    """
    max_itemset = find_max_itemset(itemsets)
    itemset_tid_dict = create_itemset_tid_dict(itemsets, max_itemset,
                                               min_support)
    write_csv(folder_path, 'itemset_tid_dict.csv', itemset_tid_dict)

    """ Make list with k, k-item set, and support
    eg [ [1, 'whole milk', 2363], ... , 
    [2, ('rice', 'rolls/buns'), 5], ... ]
    """
    k_itemsets = create_k_itemsets(itemset_tid_dict)
    write_csv(folder_path, 'k_itemsets.csv', k_itemsets,
              ['k', 'k-item set', 'Number of occurrences'])

    """ Filter out item sets that do not reach minimum support
    """
    # itemset_tid_dict_pruned = prune_itemset_tid_dict(itemset_tid_dict,
    #                                                 min_support)
    """
    
    """
    # itemset_rule_dict = create_itemset_rule_dict(dict(),
    #                                             itemset_tid_dict)

    """
    
    """
    #rule_stat_dict = create_rule_stat_dict(
    #    itemset_tid_dict, itemset_rule_dict, constraints,
    #    len(transactions_itemsets))

    end_time = time.time()
    print(round(end_time - start_time, 2), " seconds elasped")
    print('End of program.')


if __name__ == '__main__':
    main()
