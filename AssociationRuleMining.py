import csv
import time
import operator
from datetime import datetime
from itertools import combinations
from itertools import permutations

CSV_FILENAME = "Groceries_dataset.csv"
num_transactions = 0
highest_num_items_in_trans = 0
min_support = 0
min_confidence = 0
min_lift = 0


def read_csv(csv_filename):
    """
    Reads a csv file and returns csv data list
    Csv data list elements are lists representing data in each row

    :param csv_filename: eg 'filename.csv'
    :type csv_filename: str
    :return: A list with each element being another list with row data in it
        eg [ [row1col1, row1col2, ...], [row2col1, row2col2, ...], ... ]
    :rtype: list
    """
    csv_data = []
    with open(csv_filename, mode='r', encoding='latin1') as csvfile:
        read_csv = csv.reader(csvfile, dialect='excel', delimiter=',',
                              quoting=csv.QUOTE_ALL)
        for row in read_csv:
            csv_data.append(row)
    return csv_data


def sort_csv_data(csv_data):
    """
    Sorts csv data in priority of member id, then date, then item name

    :param csv_data: eg [ ['1808,21-07-2015', 'tropical fruit'],
        ['2552', '05-01-2015', 'whole milk'], ... ]
    :type csv_data: list
    :return: A list of the same csv data, but now sorted
    :rtype: list
    """
    # Sort by grocery item
    temp1 = sorted(csv_data, key=operator.itemgetter(2))
    # Sort by date
    temp2 = sorted(temp1, key=lambda d: datetime.strptime(d[1], "%d-%m-%Y"))
    # Sort by member number
    sorted_csv_data = sorted(temp2, key=operator.itemgetter(0))
    return sorted_csv_data


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
    :return: Same as input param, except duplicate grocery items removed
            eg [ ['1702','12-01-2014','2','pip fruit','yogurt'], ... ]
    :rtype: list
    """
    transactions_no_duplicates = []
    for t in transactions:
        items = list(set(t[3:]))  # remove duplicates
        items = sorted(items)  # sort again (becomes unordered for some reason)
        new_transaction = t[:3]
        new_transaction.extend(items)
        new_transaction[2] = len(new_transaction) - 3  # set new numItems
        transactions_no_duplicates.append(new_transaction)
    return transactions_no_duplicates


def write_csv(filename, csv_data):
    """ Writes csv data contained in a list to a csv file on computer

    :param filename: "outputFilename.csv"
    :type filename: str
    :param csv_data: A list with each element representing a row in a csv file
    :type csv_data: list
    """
    with open(filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_data)


# =====================================
# Eclat algorithm
# =====================================
def fillItemTidDict(items_only_transaction_list):
    item_tid_dict = dict()
    # 1-itemset
    for tid in range(0, len(items_only_transaction_list)):
        for i in range(0, len(items_only_transaction_list[tid])):
            item = items_only_transaction_list[tid][i]
            if (item not in item_tid_dict):
                item_tid_dict[item] = {tid}
            else:
                item_tid_dict[item].add(tid)
    # k-itemset, k>1
    for k in range(2, highest_num_items_in_trans + 1):
        for tid in range(0, len(items_only_transaction_list)):
            # Combinations are emitted in lexicographic sort order of input
            # items_only_transaction_list is in a-z order,
            # thus combinations will be output in same order
            comb = combinations(items_only_transaction_list[tid], k)
            comb_list = list(comb)
            for k_itemset in comb_list:
                if (k_itemset not in item_tid_dict):
                    item_tid_dict[k_itemset] = {tid}
                else:
                    item_tid_dict[k_itemset].add(tid)
    return item_tid_dict


# =====================================
# Generate itemset to association rules dict
#     key = itemset tuple
#     value = list of tuples, each tuple being association rule of form (A,C)
# =====================================
def generateItemsetAssocDict(kitemset_assoc_dict, itemset_tid_dict):
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


# =====================================
# Write results to CSV
# =====================================
def writeItemsetSupportToCsv(item_tid_dict):
    first_row = ['k', 'k-Itemset', 'NumOccurences']
    csv_lst = []
    for key, value in item_tid_dict.items():
        temp_lst = []
        if (type(key) is tuple):
            temp_lst.append(len(key))
        else:
            temp_lst.append(1)
        temp_lst.append(key)
        temp_lst.append(len(value))
        csv_lst.append(temp_lst)
    # Sort by num_occurences
    csv_lst = sorted(csv_lst, key=operator.itemgetter(2), reverse=True)
    # Sort by k
    csv_lst = sorted(csv_lst, key=operator.itemgetter(0), reverse=False)

    for k in range(1, highest_num_items_in_trans + 1):
        output_fname = str(k) + 'Itemset_Support.csv'
        with open(output_fname, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(first_row)
            while (True):
                if (csv_lst[0][0] > k):
                    break
                popped = csv_lst.pop(0)
                csvwriter.writerow(popped)
                if (len(csv_lst) == 0):
                    break


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


def promptUser():
    min_support = int(input("Enter minimum support (integer): "))
    min_confidence = float(input('Enter minimum confidence (double): '))
    min_lift = float(input('Enter minimum lift (double): '))
    return min_support, min_confidence, min_lift


def main():
    global num_transactions, highest_num_items_in_trans
    global min_support, min_confidence, min_lift
    result_folder = "results"

    # Set minimum support, confidence, and lift values from user input
    min_support, min_confidence, min_lift = promptUser();
    start_time = time.time()

    # Read CSV file and put data in a list then sort the list
    csv_data = read_csv(CSV_FILENAME)
    csv_data = csv_data[1:]  # remove field name row
    sorted_csv_data = sort_csv_data(csv_data)

    # Create transactions list out of sorted csv data
    # Duplicate CSV items are in this list
    transactions = create_transactions(sorted_csv_data)
    write_csv("results/transactions_duplicates.csv", transactions)
    # Remove duplicate csv items from transactions list
    transactions_no_duplicates = remove_duplicates(transactions)
    write_csv(result_folder + "/transactions_no_duplicates.csv",
              transactions_no_duplicates)

    """
    # =====================================================
    # Process transactionToItemset list into item_tid_dict
    # Also process into 2-itemset tid dict, over MIN_SUPP
    # =====================================================
    eclat_start_time = time.time()
    itemset_tid_dict = fillItemTidDict(items_in_transaction_list)
    writeItemsetSupportToCsv(itemset_tid_dict)
    pruned_itemset_tid_dict = dict()
    prunedDictSize = 0
    for key, value in itemset_tid_dict.items():
        if ((type(key) is tuple) & (len(value) >= min_support)):
            pruned_itemset_tid_dict[key] = value
            prunedDictSize += 1
    print('prunedDictSize=', prunedDictSize)
    kitemset_assoc_dict = generateItemsetAssocDict(dict(),
                                                   pruned_itemset_tid_dict)

    # =====================================================
    # Generate association rules and store as CSV
    # =====================================================
    assoc_stat_dict = generateAssocStatDict(itemset_tid_dict,
                                            kitemset_assoc_dict)
    eclat_end_time = time.time()
    writeAssocStatDictToCsv('Association_Rules.csv', assoc_stat_dict)

    # =====================================================
    # End of program, wrapup
    # =====================================================
    eclat_elasped = eclat_end_time - eclat_start_time
    eclat_elasped = round(eclat_elasped, 2)

    total_end_time = time.time()
    total_elasped = total_end_time - start_time
    total_elasped = round(total_elasped, 2)
    print('Time elasped for eclat=' + str(eclat_elasped) + 's')
    print('Time elasped for entire program=' + str(total_elasped) + 's')
    print("End of program.")
    """

if __name__ == "__main__":
    main()