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


def prompt_constraints():
    """ Prompts user for constraints of min support, min confidence and min
    lift, min support will affect association rule generation and min
    confidence/min lift will affect filtering of association rules that were
    generated

    :return: Tuple with min support, min confidence, min lift
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
    In case of list, each inner list represents a row
    In case of dict, keys go on col1 and vals go on col2

    :param folder_path: Full path to where you want csv file written
    :type folder_path: str
    :param filename: Filename of csv file you want written
    :type filename: str
    :param data:
    :type data: list or dict
    :param header: The first row
    :type header: list, optional
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)  # create folder is not exists
    write_path = os.path.join(folder_path, filename)
    with open(write_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        if header is not None:
            csv_writer.writerow(header)  # write header
        if type(data) == list:
            csv_writer.writerows(data)
        if type(data) == dict:
            for i in data.items():
                csv_writer.writerow(i)


def create_transactions(csv_data):
    """ Dependent on create_verbose_trans_list(), filter_verbose_trans_list()
    1) Creates verbose transactions list
    2) Removes all duplicate items
    3) Strips all data besides item names
    a verbose transactions list looks like:
    [ [member_number, date, num_items, item1, item1, item2, ... ], ... ]
    a transactions list looks like :
    [ [item1, item2, ...], ...]

    :param csv_data: List containing csv data, 1 item per row
        eg [ ['1808,21-07-2015', 'tropical fruit'],
        ['2552', '05-01-2015', 'whole milk'], ... ]
    :type csv_data: list
    :return: List containing lists of transaction
        eg [ ['pip fruit','yogurt'], ... ]
    :rtype: list
    """
    # eg [ ['1702','12-01-2014','3','pip fruit','yogurt,'yogurt'], ... ]
    verbose_trans_list = create_verbose_trans_list(csv_data)
    # eg [ ['1702','12-01-2014','2','pip fruit','yogurt], ... ]
    verbose_trans_list = filter_verbose_trans_list(verbose_trans_list)
    # eg [ ['pip fruit','yogurt'], ... ]
    transactions = []
    for tran in verbose_trans_list:
        transactions.append(tran[3:])
    return transactions


def create_verbose_trans_list(csv_data):
    """ Helper for create_transactions()

    :param csv_data: List containing data of each row of csv file that is read
        There should be a member number, date, and single item in each row
    :return: List containing member number, date, number of items, and item
        names
    :rtype: list
    """
    verbose_trans_list = []
    trans = csv_data[0]  # first transaction to add csv items to
    for i in range(1, len(csv_data)):
        csv_number = csv_data[i][0]  # member number
        csv_date = csv_data[i][1]
        csv_item = csv_data[i][2]
        trans_number = trans[0]
        trans_date = trans[1]
        # member id or date are different, so we add our built up transaction
        # to transaction_list and create a new transaction that we can
        # add csv_items onto
        if (trans_number != csv_number) or (trans_date != csv_date):
            num_items = len(trans) - 2
            trans.insert(2, str(num_items))
            verbose_trans_list.append(trans)
            trans = [csv_number, csv_date, csv_item]
        # member id and date are same, so add csv_item onto transaction
        else:
            trans.append(csv_item)
    num_items = len(trans) - 2
    trans.insert(2, str(num_items))
    verbose_trans_list.append(trans)
    return verbose_trans_list


def filter_verbose_trans_list(verbose_trans_list):
    """ Helper for create_transactions()
    Removes all duplicate grocery items in a verbose transactions list

    :param verbose_trans_list: List with transaction data, with duplicates
        eg [ ['1702','12-01-2014','3','pip fruit','yogurt','yogurt'], ... ]
    :type verbose_trans_list: list
    :return: Same as input list, except duplicate items are now gone
        eg [ ['1702','12-01-2014','2','pip fruit','yogurt'], ... ]
    :rtype: list
    """
    verbose_trans_no_duplicates = []
    for tran in verbose_trans_list:
        itemset = list(set(tran[3:]))  # remove duplicates
        # sort again (becomes unordered for some reason)
        itemset = sorted(itemset)
        new_transaction = tran[:3]
        new_transaction.extend(itemset)
        # set num items in itemset
        new_transaction[2] = len(new_transaction) - 3
        verbose_trans_no_duplicates.append(new_transaction)
    return verbose_trans_no_duplicates


def create_itemset_tid_dict(trans, min_support):
    """ dependent on create_item_tid_dict(), create_combs(),
    create_next_k_itemset_tid_dict()
    Creates dictionary with keys of frequent itemsets and vals of tidsets
    associated with frequent itemsets

    :param trans: List containing list of transactions
    :type trans: list
    :param min_support:
    :type min_support: int
    :return: Frequent itemset to tidset dictionary
    :rtype: dict
    """
    # Make single item to tidset dictionary
    # This will continually be referenced
    # eg { 'pastry': {0, 4096, ... }, 'whole milk': {0, 1, ...}, ... }
    item_tidset_dict = create_item_tid_dict(trans)
    # This holds k-itemset tidset dict that will be joined with return dict
    # once we properly generate and filter it
    k_itemset_tidset_dict = item_tidset_dict.copy()
    k = 1
    full_itemset_tid_dict = dict()  # return dictionary

    while True:  # Loop until no more itemset-tidset pairs can be combined
        # 1) Filter out entries below minimum support
        k_itemset_tidset_dict = dict(
            filter(
                lambda entry: len(entry[1]) >= min_support,
                k_itemset_tidset_dict.items()
            )
        )
        # 2) Create all itemset combinations
        combs = create_combs(k, k_itemset_tidset_dict)
        # 3) Generate next k itemset dictionary
        next_k_itemset_tid_dict = create_next_k_itemset_tid_dict(
            combs, item_tidset_dict, min_support)

        # No combinations above minimum support were generated
        if len(next_k_itemset_tid_dict) == 0:
            break
        full_itemset_tid_dict.update(next_k_itemset_tid_dict)
        k_itemset_tidset_dict = next_k_itemset_tid_dict.copy()
        k += 1
    return full_itemset_tid_dict


def create_item_tid_dict(trans):
    """ helper for create_itemset_tid_dict()
    Creates and returns a item to tidset dict

    :param trans: List containing lists of transaction
        eg [ ['soda', 'whole milk'], ... ]
    :type trans: list
    :return: Key of single item, val of tidset
        eg { 'soda': {2, 6, ...}, ... }
    :rtype: dict
    """
    item_tid_dict = dict()
    for tid in range(0, len(trans)):
        an_itemset = trans[tid]  # eg ['pastry','salty snack','whole milk']
        for i in range(0, len(an_itemset)):
            item = an_itemset[i]
            if item not in item_tid_dict:
                item_tid_dict[item] = {tid}
            else:  # add onto existing key
                item_tid_dict[item].add(tid)
    return item_tid_dict


def create_combs(k, k_itemset_tidset_dict):
    """ helper for create_itemset_tid_dict()
    Create all possible combinations of k length from keys of itemsets
    in k_itemset_tidset_dict

    :param k: Number of items in itemset
    :type k: int
    :param k_itemset_tidset_dict:
        eg k=1 { 'soda': {2, 6, ...}, ... }
        eg k>2 { ('beverages', 'soda'): {12038, 10125, ...}, ... }
    :type k_itemset_tidset_dict: dict
    :return: List of all possible combinations of items that can be made from
        itemset keys
    :rtype: list
    """
    if k == 1:
        items_list = list(k_itemset_tidset_dict.keys())
    else:
        items_list = set()  # set ensures no repeat items
        for itemset in k_itemset_tidset_dict.keys():
            for item in itemset:
                items_list.add(item)
        items_list = list(items_list)
    combs = list(combinations(items_list, k))
    return combs


def create_next_k_itemset_tid_dict(combs, item_tidset_dict, min_support):
    """ helper for create_itemset_tid_dict()
    Uses combinations generated from current k itemset tidset dict to
    create next k itemset tidset dict

    :param combs: List of all possible combinations of itemsets possible from
        current k_itemset_tid_dict
    :type combs: list
    :param item_tidset_dict:
    :type item_tidset_dict: dict
    :param min_support: If tidset length below min support, filter it out
    :type min_support: int
    :return:
    :rtype: dict
    """
    next_k_itemset_tid_dict = dict()
    for a_comb in combs:
        item0 = a_comb[0]  # first combination
        # initialize tidset with first tidset
        tidsets_intersect = item_tidset_dict[item0]
        for i in range(1, len(a_comb)):
            next_item = a_comb[i]
            next_tidset = item_tidset_dict[next_item]
            tidsets_intersect = tidsets_intersect.intersection(next_tidset)
        if len(tidsets_intersect) >= min_support:
            next_k_itemset_tid_dict[a_comb] = tidsets_intersect
    return next_k_itemset_tid_dict

# Backup
"""
# TODO: Fix single items being present in return dict
def create_itemset_tid_dict(itemsets, min_support):
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
    k = 1
    k_itemset_tid_dict = item_tid_dict.copy()  # aka kitemset dict
    full_itemset_tid_dict = dict()
    # TODO: this is related to why single items are repeated in dict
    # full_itemset_tid_dict.update(k_itemset_tid_dict)
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
        combs = list(combinations(items_list, k))
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
"""

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
    trans = create_transactions(sorted_csv_data)
    write_csv(folder_path, 'trans.csv', trans)

    """ Map all combinations of item sets to transaction id (tid) sets
    tids match the indexes where you can find item set in itemsets list
    eg { 'rubbing alcohol': {5348, 13062, 14833, 7443, 6739},
        ('detergent', 'pork'): {196, 14397, 4486}, ... }
    """
    itemset_tid_dict = create_itemset_tid_dict(trans, min_support)
    write_csv(folder_path, 'itemset_tid_dict.csv', itemset_tid_dict)

    """ Make list with k, k-item set, and support
    eg [ [1, 'whole milk', 2363], ... , 
    [2, ('rice', 'rolls/buns'), 5], ... ]
    """
    k_itemsets = create_k_itemsets(itemset_tid_dict)
    write_csv(folder_path, 'k_itemsets.csv', k_itemsets,
              ['k', 'k-item set', 'Number of occurrences'])
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
    print(round(end_time - start_time, 2), ' seconds total runtime')
    print('End of program.')


if __name__ == '__main__':
    main()
