import csv
import operator
import os
import time
from datetime import datetime
from itertools import combinations

CSV_FILENAME = 'grocery_data.csv'  # needs csv in same directory as py file
RESULT_FOLDER = 'results'  # will create folder in same directory as py file
DEV_FOLDER = 'dev'  # will create folder in same directory as py file


def prompt_constraints():
    """ Prompts user for constraints of min support, min confidence and min
    lift

    :return: tuple (min_support, min_confidence, min_lift)
    :rtype: (int, float, float)
    """
    min_support = int(input('Enter minimum support (int): '))
    min_confidence = float(input('Enter minimum confidence(A->C) (float): '))
    min_lift = float(input('Enter minimum lift(A->C) (float): '))
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

    :param csv_data: eg [ ['1808', '21-07-2015', 'tropical fruit'],
        ['2552', '05-01-2015', 'whole milk'], ... ]
    :type csv_data: list
    :return: Same as input param except sorted by grocery item, then date,
        then member number
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
    2) Removes all duplicate items from verbose transactions list
    3) Strips all data besides item names, so now we have transactions list
    a verbose transactions list looks like:
    [ [member_number, date, num_items, item1, item1, item2, ... ], ... ]
    a transactions list looks like :
    [ [item1, item2, ...], ...]

    :param csv_data: List containing csv data, 1 item per row
        eg [ ['1808,21-07-2015', 'tropical fruit'],
        ['2552', '05-01-2015', 'whole milk'], ... ]
    :type csv_data: list
    :return: List of transactions
        A transaction being all items with matching customer number and date
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

    :param csv_data: create_transactions() passes param
    :return: eg [ [member_number, date, num_items, item1, item1, item2, ... ]
        , ... ]
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


def create_item_tidset_dict(trans):
    """ Creates and returns a item to tidset dict

    :param trans: List containing lists of transaction
        eg [ ['soda', 'whole milk'], ... ]
    :type trans: list
    :return: Key of single item, val of tidset
        eg { 'soda': {2, 6, ...}, ... }
    :rtype: dict
    """
    item_tidset_dict = dict()
    for tid in range(0, len(trans)):
        an_itemset = trans[tid]  # eg ['pastry','salty snack','whole milk']
        for i in range(0, len(an_itemset)):
            item = an_itemset[i]
            if item not in item_tidset_dict:
                item_tidset_dict[item] = {tid}
            else:  # add onto existing key
                item_tidset_dict[item].add(tid)
    return item_tidset_dict


def create_itemset_tidset_dict(item_tidset_dict, min_support):
    """ dependent on create_combs(), create_next_k_itemset_tid_dict()
    Creates dictionary with keys of frequent itemsets and vals of tidsets
    associated with frequent itemsets

    :param item_tidset_dict:
    :type item_tidset_dict: dict
    :param min_support: If below minimum support, filter away
    :type min_support: int
    :return: Frequent itemset to tidset dictionary
    :rtype: dict
    """
    # This holds k-itemset tidset dict that will be joined with return dict
    # once we properly generate and filter it, filtering will be done by
    # set intersection
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


def create_itemset_rule_dict(itemset_tid_dict):
    """ Create association rules from frequent itemsets

    :param itemset_tid_dict: Key of itemset, val of tidset
    :type itemset_tid_dict: dict
    :return: Key of itemset tuple, val of list of rules, rule being of form
        tuple (antecedent, consequent)
        eg {('ham', 'whole milk'):
            [({'ham'}, {'whole milk'}), ({'whole milk'}, {'ham'}), ...] }
        ('soda', 'rolls/buns', 'whole milk'):
            [({'soda'}, {'whole milk', 'rolls/buns'}),
            ({'rolls/buns'}, {'soda', 'whole milk'}),
            ({'whole milk'}, {'soda', 'rolls/buns'}),
            ({'soda', 'rolls/buns'}, {'whole milk'}),
            ({'soda', 'whole milk'}, {'rolls/buns'}),
            ({'whole milk', 'rolls/buns'}, {'soda'})], ... }
    :rtype: dict
    """
    itemset_rule_dict = dict()
    for itemset, tidset in itemset_tid_dict.items():
        if len(itemset) > 1:  # 1-itemset can't form a rule
            rule_list = []
            for i in range(1, len(itemset)):
                # Find possible combinations
                combs_list = list(combinations(itemset, i))
                for j in range(0, len(combs_list)):
                    antecedent = set(combs_list[j])
                    # Itemset can be thought of set(A) + set(C)
                    # So we can use some set math to isolate consequent
                    consequent = set(itemset) - antecedent
                    rule = (antecedent, consequent)
                    rule_list.append(rule)
            itemset_rule_dict[itemset] = rule_list
    return itemset_rule_dict


def create_rule_stat_dict(item_tidset_dict, itemset_rule_dict,
                          constraints, num_trans):
    """ Dependent on find_intersection()

    :param item_tidset_dict:
    :type item_tidset_dict: dict
    :param itemset_rule_dict:
    :type itemset_rule_dict: dict
    :param constraints: Tuple (min_support, min_confidence, min_lift)
    :type constraints: tuple
    :param num_trans: Length of transactions list
    :type num_trans: int
    :return: format `{(antecedent_tuple, consequent_tuple):
        (support, confidence, lift), ...}`
        eg {(('frankfurter',), ('other vegetables',)):
        (0.0051, 0.1363, 1.1163), ...}
    :rtype: dict
    """
    min_supp = constraints[0] / num_trans
    min_conf = constraints[1]
    min_lift = constraints[2]
    rule_stat_dict = dict()

    for itemset, assoc_rules in itemset_rule_dict.items():
        for rule in assoc_rules:
            ante = rule[0]
            cons = rule[1]
            ante_tidset = find_intersection(ante, item_tidset_dict)
            cons_tidset = find_intersection(cons, item_tidset_dict)
            joined_tidset = ante_tidset.intersection(cons_tidset)
            num_ante = len(ante_tidset)
            num_cons = len(cons_tidset)
            num_joined = len(joined_tidset)
            supp = num_joined / num_trans
            conf = num_joined / num_ante
            lift = conf / (num_cons / num_trans)
            supp = round(supp, 4)
            conf = round(conf, 4)
            lift = round(lift, 4)
            if supp >= min_supp and conf >= min_conf and lift >= min_lift:
                rule_stat_dict[(tuple(ante), tuple(cons))] = (supp, conf, lift)
    return rule_stat_dict


def find_intersection(itemset, item_tidset_dict):
    """ Helper for create_rule_stat_dict()

    :param itemset:
    :type itemset: set
    :param item_tidset_dict:
    :type item_tidset_dict: dict
    :return: tidset containing all tids where itemset can be found
    :rtype: set
    """
    inter_tidset = set()
    for item in itemset:
        tidset = item_tidset_dict[item]
        if len(inter_tidset) == 0:  # can't intersect without something
            inter_tidset = inter_tidset.union(tidset)
        else:  # we have at least 1 tidset added, now we can intersect
            inter_tidset = inter_tidset.intersection(tidset)
    return inter_tidset


def create_rule_stat_list(rule_stat_dict):
    """ Creates a pretty list to be written on csv file our final results

    :param rule_stat_dict:
    :type rule_stat_dict: dict
    :return:
    :rtype: list
    """
    rule_stat_list = []
    for rule, stat in rule_stat_dict.items():
        ante, cons = rule[0], rule[1]
        supp, conf, lift = stat[0], stat[1], stat[2]
        k = len(ante) + len(cons)
        rule_stat_list.append([k, len(ante), ante, len(cons), cons,
                               supp, conf, lift])
    # Sort by lift
    rule_stat_list = sorted(rule_stat_list, key=operator.itemgetter(7))
    # Sort by k size
    rule_stat_list = sorted(rule_stat_list, key=operator.itemgetter(0))
    return rule_stat_list


def main():
    # min_support, min_confidence, min_lift = (15, .10, 1.00)
    # constraints = (min_support, min_confidence, min_lift)
    constraints = prompt_constraints()
    start_time = time.time()
    min_support, min_confidence, min_lift = \
        constraints[0], constraints[1], constraints[2]
    dev_path = os.path.join(os.getcwd(), DEV_FOLDER)
    result_path = os.path.join(os.getcwd(), RESULT_FOLDER)

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
    write_csv(dev_path, '1_trans.csv', trans)

    """ Make single item to tidset dictionary, we will reference this a lot
    # eg { 'pastry': {0, 4096, ... }, 'whole milk': {0, 1, ...}, ... }
    """
    item_tidset_dict = create_item_tidset_dict(trans)
    write_csv(dev_path, '2_item_tidset_dict.csv', item_tidset_dict)

    """ Map all combinations of item sets to transaction id (tid) sets
    tids match the indexes where you can find item set in itemsets list
    eg { 'rubbing alcohol': {5348, 13062, 14833, 7443, 6739},
        ('detergent', 'pork'): {196, 14397, 4486}, ... }
    """
    itemset_tidset_dict = create_itemset_tidset_dict(item_tidset_dict,
                                                     min_support)
    write_csv(dev_path, '3_itemset_tidset_dict.csv', itemset_tidset_dict)

    """ Make list with k, k-item set, and support
    eg [ [1, 'whole milk', 2363], ... , 
    [2, ('rice', 'rolls/buns'), 5], ... ]
    """
    k_itemsets = create_k_itemsets(itemset_tidset_dict)
    write_csv(dev_path, '4_k_itemsets.csv', k_itemsets,
              ['k', 'k-item set', 'Number of occurrences'])

    """
    
    """
    itemset_rule_dict = create_itemset_rule_dict(itemset_tidset_dict)
    write_csv(dev_path, '5_itemset_rule_dict.csv', itemset_rule_dict)

    """
    
    """
    rule_stat_dict = create_rule_stat_dict(item_tidset_dict, itemset_rule_dict,
                                           constraints, len(trans))
    write_csv(dev_path, '6_rule_stat_dict.csv', rule_stat_dict)

    rule_stat_list = create_rule_stat_list(rule_stat_dict)
    write_csv(result_path, 'rule_stat_list.csv', rule_stat_list,
              ['Size(A+C)', 'Size(A)', 'Antecedent',
               'Size(C)', 'Consequent',
               'Support(A->C)', 'Confidence(A->C)', 'Lift(A->C)'])

    end_time = time.time()
    print(round(end_time - start_time, 2), ' seconds total runtime')
    print('End of program.')


if __name__ == '__main__':
    main()
