# This program processes grocery store data in CSV file
# Then it generates association rules using the ECLAT algorithm
# It outputs association rules to a newly written CSV file

CSV_FNAME = "Groceries_dataset.csv"
NUM_TRANSACTIONS = 0
HIGHEST_NUM_ITEMS_IN_TRANS = 0

MIN_SUPPORT = 0
MIN_CONFIDENCE = 0
MIN_LIFT = 0

import csv
import time
import operator
from datetime import datetime
from collections import OrderedDict
from itertools import combinations
from itertools import permutations

# =========================================================
# CSV Reading/Writing
# =========================================================
def readCsv(fname):
    field_list = []
    data_list = []
    with open(fname, mode='r', encoding='latin1') as csvfile: 
        read_csv = csv.reader(csvfile, dialect='excel', delimiter = ',', quoting=csv.QUOTE_ALL)
        for row in read_csv: # Get the first row (has field names)
            field_list.append(row[0])
            field_list.append(row[1])
            field_list.append(row[2])
            break
        for row in read_csv:
            data_list.append(row)
    return field_list, data_list

def writeCsv(writeFname, data_list, field_list):
    with open(writeFname, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(field_list)
        for item in data_list:
            csvwriter.writerow(item)
# =========================================================
# Get data from CSV
# =========================================================
def sortDataList(data_list):
    # Sort by grocery item
    sorted_data_list1 = sorted(data_list,key=operator.itemgetter(2))
    # Sort by date
    sorted_data_list2 = sorted(sorted_data_list1,key=lambda d: datetime.strptime(d[1], "%d-%m-%Y"))
    # Sort by member number
    sorted_data_list3 = sorted(sorted_data_list2,key=operator.itemgetter(0))
    return sorted_data_list3
# =========================================================
# Turn original CSV data into transaction list
# =========================================================
def createFullTransactionList(data_list):
    trans_list = [] # trans_list is a list containing a all t
    one_trans = data_list[0] # start off with first row read
    data_list_len = len(data_list)

    for i in range(1, data_list_len):
        member_number = data_list[i][0]
        date = data_list[i][1]
        grocery_item = data_list[i][2]

        # If member number or date is different, add the built up transaction
        # to the list of all transactions, then create a new empty transaction,
        # then append member_number, date, grocery_item
        if((one_trans[0] != member_number) or (one_trans[1] != date)):
            num_items = len(one_trans) - 2
            one_trans.insert(2,str(num_items))
            trans_list.append(one_trans)
            one_trans = []
            one_trans.append(member_number)
            one_trans.append(date)
            one_trans.append(grocery_item)
        # else member number and date are same, so just add item to 
        # the current transaction we are building up
        else: 
            one_trans.append(grocery_item)
    num_items = len(one_trans) - 2
    one_trans.insert(2,str(num_items))
    trans_list.append(one_trans)
    return trans_list
# =====================================
# Eclat algorithm
# =====================================
def fillItemTidDict(items_only_transaction_list):
    item_tid_dict = dict()
    # 1-itemset
    for tid in range(0, len(items_only_transaction_list)):
        for i in range(0, len(items_only_transaction_list[tid])):
            item = items_only_transaction_list[tid][i]
            if(item not in item_tid_dict):
                item_tid_dict[item]={tid}
            else:
                item_tid_dict[item].add(tid)
    # k-itemset, k>1
    for k in range(2, HIGHEST_NUM_ITEMS_IN_TRANS+1):
        for tid in range(0, len(items_only_transaction_list)):
            # Combinations are emitted in lexicographic sort order of input
            # items_only_transaction_list is in a-z order,
            # thus combinations will be output in same order
            comb = combinations(items_only_transaction_list[tid],k)
            comb_list = list(comb)
            for k_itemset in comb_list:
                if(k_itemset not in item_tid_dict):
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
        kitemset_assoc_dict[itemset] =  assoc_rule_lst
        assoc_rule_lst = []
    return kitemset_assoc_dict
# =====================================
# Generate association rule to statistics dictionary
#   key = tuple of form (A,C)
#   value = tuple of form (support(A->C),confidence(A->C),lift(A->C))
# =====================================
def generateAssocStatDict(itemset_tid_dict, kitemset_assoc_dict):
    assoc_stat_dict = dict()
    for key,value in kitemset_assoc_dict.items():
        support_a_c = len(itemset_tid_dict[key])/NUM_TRANSACTIONS
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
                        support_a = len(itemset_tid_dict[p]) / NUM_TRANSACTIONS
                        break
            else:
                support_a = len(itemset_tid_dict[antecedent]) / NUM_TRANSACTIONS
            # rearrange consequent until it gets a match in itemset_tid_dict
            if(consequent not in itemset_tid_dict):
                perm = permutations(consequent,len(consequent))
                list_perm = list(perm)
                for p in list_perm:
                    if(p in itemset_tid_dict):
                        support_c = len(itemset_tid_dict[p]) / NUM_TRANSACTIONS
                        break
            else:
                support_c = len(itemset_tid_dict[consequent]) / NUM_TRANSACTIONS
            confidence_a_c = support_a_c/support_a
            lift_a_c = confidence_a_c/support_c
            # prune out rules below mins
            if ( (confidence_a_c < MIN_CONFIDENCE ) | (lift_a_c < MIN_LIFT)):
                continue
            # round off
            support_a_c = round(support_a_c,4)
            confidence_a_c = round(confidence_a_c,4)
            lift_a_c = round(lift_a_c, 4)
            assoc_stat_dict[assoc_rule] = [support_a_c,confidence_a_c,lift_a_c]
    return assoc_stat_dict

# =====================================
# Write results to CSV
# =====================================
def writeItemsetSupportToCsv(item_tid_dict):
    first_row = ['k','k-Itemset','NumOccurences']
    csv_lst = []
    for key,value in item_tid_dict.items():
        temp_lst = []
        if(type(key) is tuple):
            temp_lst.append(len(key))
        else:
            temp_lst.append(1)
        temp_lst.append(key)
        temp_lst.append(len(value))
        csv_lst.append(temp_lst)
    # Sort by num_occurences
    csv_lst = sorted(csv_lst,key=operator.itemgetter(2),reverse=True)
    # Sort by k
    csv_lst = sorted(csv_lst,key=operator.itemgetter(0),reverse=False)

    for k in range(1, HIGHEST_NUM_ITEMS_IN_TRANS+1):
        output_fname = str(k) + 'Itemset_Support.csv'
        with open(output_fname, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(first_row)
            while(True):
                if(csv_lst[0][0]>k):
                    break
                popped = csv_lst.pop(0)
                csvwriter.writerow(popped)
                if(len(csv_lst)==0):
                    break

def writeAssocStatDictToCsv(output_fname, assoc_stat_dict):
    first_row = ['Itemset Size','Antecedent','Consequent',
                'support(A->C)','confidence(A->C)','lift(A->C)']
    csv_lst = []
    for key,value in assoc_stat_dict.items():
        temp_lst = []
        temp_lst.append(len(key[0])+len(key[1]))
        temp_lst.append(key[0]) # antecedent
        temp_lst.append(key[1]) # consequent
        temp_lst.append(value[0]) # support(A->C)
        temp_lst.append(value[1]) # confidence(A->C)
        temp_lst.append(value[2]) # lift (A->C)
        csv_lst.append(temp_lst)
    # Sort by confidence
    csv_lst = sorted(csv_lst,key=operator.itemgetter(4),reverse=True)
    # Sort itemset size
    csv_lst = sorted(csv_lst,key=operator.itemgetter(0),reverse=True)
    with open(output_fname, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(first_row)
        for row in csv_lst:
            csvwriter.writerow(row)

def main():
    global NUM_TRANSACTIONS, HIGHEST_NUM_ITEMS_IN_TRANS
    global MIN_SUPPORT, MIN_CONFIDENCE, MIN_LIFT
    MIN_SUPPORT = int(input("Enter MIN_SUPPORT(integer): "))
    MIN_CONFIDENCE = float(input('Enter MIN_CONFIDENCE(double): '))
    MIN_LIFT = float(input('Enter MIN_LIFT(double): '))
    total_start_time = time.time()
    # =====================================================
    # Process CSV into transaction CSV with duplicates
    # =====================================================
    field_list, data_list = readCsv(CSV_FNAME)
    items_only_data_list = []
    sorted_data_list = sortDataList(data_list)
    csv_duplicate_list = createFullTransactionList(sorted_data_list)
    NUM_TRANSACTIONS = len(csv_duplicate_list)
    print('NUM_TRANSACTIONS='+str(NUM_TRANSACTIONS))
    # =====================================================
    # Process CSV into transaction CSV with NO duplicates
    # =====================================================
    items_in_transaction_list = [] # No duplicates
    HIGHEST_NUM_ITEMS_IN_TRANS = 0
    for t in csv_duplicate_list:
        only_t = list(set(t[3:]))
        len_only_t = len(only_t)
        if(len_only_t > HIGHEST_NUM_ITEMS_IN_TRANS):
            HIGHEST_NUM_ITEMS_IN_TRANS = len_only_t
        items_in_transaction_list.append(sorted(only_t))
    csv_no_duplicate_list = []
    for i in range(0, len(csv_duplicate_list)):
        new_t = csv_duplicate_list[i][:3]
        new_t.extend(items_in_transaction_list[i])
        new_t[2] = len(new_t)-3
        csv_no_duplicate_list.append(new_t)
    print("HIGHEST_NUM_ITEMS_IN_TRANS="+str(HIGHEST_NUM_ITEMS_IN_TRANS))
    new_field_list = ["CustomerID","Date of purchase","no_of_items(k)"]
    for i in range(1, HIGHEST_NUM_ITEMS_IN_TRANS+1):
        new_field_list.append(str(i))
    writeCsv("Transactions_No_Duplicates.csv",csv_no_duplicate_list,new_field_list)
    # =====================================================
    # Process transactionToItemset list into item_tid_dict
    # Also process into 2-itemset tid dict, over MIN_SUPP
    # =====================================================
    eclat_start_time = time.time()
    itemset_tid_dict = fillItemTidDict(items_in_transaction_list)
    writeItemsetSupportToCsv(itemset_tid_dict)
    pruned_itemset_tid_dict = dict()
    prunedDictSize = 0
    for key,value in itemset_tid_dict.items():
        if( (type(key) is tuple) & (len(value) >= MIN_SUPPORT) ):
            pruned_itemset_tid_dict[key] = value
            prunedDictSize += 1
    print('prunedDictSize=',prunedDictSize)
    kitemset_assoc_dict = generateItemsetAssocDict(dict(), pruned_itemset_tid_dict)

    # =====================================================
    # Generate association rules and store as CSV
    # =====================================================
    assoc_stat_dict = generateAssocStatDict(itemset_tid_dict, kitemset_assoc_dict)
    eclat_end_time = time.time()
    writeAssocStatDictToCsv('Association_Rules.csv', assoc_stat_dict)

    # =====================================================
    # End of program, wrapup
    # =====================================================
    eclat_elasped = eclat_end_time - eclat_start_time
    eclat_elasped = round(eclat_elasped,2)

    total_end_time = time.time()
    total_elasped = total_end_time - total_start_time
    total_elasped = round(total_elasped,2)
    print('Time elasped for eclat=' + str(eclat_elasped) + 's')
    print('Time elasped for entire program=' + str(total_elasped) +'s')
    print("End of program.")

if __name__ == "__main__":
    main()