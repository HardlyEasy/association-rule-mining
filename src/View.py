from typing import *
import operator
import os
import csv


class View:
    # creates folder path if not already exists
    RESULT_PATH = os.path.join(os.getcwd(), 'results')

    def prompt_constraints(self):
        """ Asks for and returns minimum support, confidence, lift
        """
        min_supp = int(input('Enter min support (int): '))
        min_conf = float(input('Enter min confidence(A->C) (float): '))
        min_lift = float(input('Enter min lift(A->C) (float): '))
        constraints = (min_supp, min_conf, min_lift)
        return constraints

    def write_csv(self, out_filename: str, data: Union[List, Dict],
                  header=None):
        """Data from List or Dict gets written to CSV file
        header is first line to be written to CSV file
        """
        if not os.path.exists(self.RESULT_PATH):
            os.makedirs(self.RESULT_PATH, exist_ok=True)
        write_path = os.path.join(self.RESULT_PATH, out_filename)
        with open(write_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            if header is not None:
                csv_writer.writerow(header)  # write header
            if type(data) == list:
                csv_writer.writerows(data)
            if type(data) == dict:
                for i in data.items():
                    csv_writer.writerow(i)

    def write_frequency(self, csv_filename, itemset_tidset_dict):
        """Finds number of occurrences of k-itemsets and writes them
        """
        itemset_frequency = []
        for key, value in itemset_tidset_dict.items():
            temp_list = []
            if type(key) is tuple:
                temp_list.append(len(key))  # k
            else:
                temp_list.append(1)
            temp_list.append(key)  # k-item set
            temp_list.append(len(value))  # number of occurrences
            itemset_frequency.append(temp_list)
        # Sort by number of occurrences
        itemset_frequency = sorted(itemset_frequency,
                                   key=operator.itemgetter(2), reverse=True)
        # Sort by k
        itemset_frequency = sorted(itemset_frequency,
                                   key=operator.itemgetter(0), reverse=False)
        self.write_csv(csv_filename, itemset_frequency)

    def write_rule_stat(self, csv_filename, rule_stat_dict):
        """Writes rule stat dict data nicely
        """
        rule_stat_list = []
        for rule, stat in rule_stat_dict.items():
            ante, cons = rule[0], rule[1]
            supp, conf, lift = stat[0], stat[1], stat[2]
            k = len(ante) + len(cons)
            rule_stat_list.append([k, len(ante), len(cons), ante, cons,
                                   supp, conf, lift])
        # Sort by lift
        rule_stat_list = sorted(rule_stat_list, key=operator.itemgetter(7),
                                reverse=True)
        # Sort by size(A+C)
        rule_stat_list = sorted(rule_stat_list, key=operator.itemgetter(0),
                                reverse=True)
        self.write_csv(csv_filename, rule_stat_list,
                       ['Size(A+C)', 'Size(A)', 'Size(C)', 'A', 'C',
                        'Supp(A->C)', 'Conf(A->C)', 'Lift(A->C)'])
