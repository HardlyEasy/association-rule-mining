from typing import *
from datetime import datetime
import operator
import os
import csv
import json


class Model:
    """Each instance stores data related to a CSV file being mined
    """
    GROCERY_PATH = os.path.join(os.getcwd(), '..', 'input')
    SETTINGS = json.load(open(os.path.join(os.getcwd(), '..',
                                           'settings.json')))

    def __init__(self, filename: str):
        self.filename = filename
        self.min_supp = self.SETTINGS['constraints']['min_supp']
        self.min_conf = self.SETTINGS['constraints']['min_conf']
        self.min_lift = self.SETTINGS['constraints']['min_lift']
        # Blanks
        self.csv_data = []
        self.trans = []  # transactions list
        self.item_tidset_dict = dict()
        self.itemset_tidset_dict = dict()
        self.itemset_rule_dict = dict()
        self.rule_stat_dict = dict()

    def set_csv_data(self, csv_data: List[List[str]]):
        self.csv_data = csv_data

    def set_trans(self, trans: List[List[str]]):
        self.trans = trans

    def set_item_tidset_dict(self, item_tidset_dict: Dict):
        self.item_tidset_dict = item_tidset_dict

    def set_itemset_tidset_dict(self, itemset_tidset_dict: Dict):
        self.itemset_tidset_dict = itemset_tidset_dict

    def set_itemset_rule_dict(self, itemset_rule_dict: Dict):
        self.itemset_rule_dict = itemset_rule_dict

    def set_rule_stat_dict(self, rule_stat_dict: Dict):
        self.rule_stat_dict = rule_stat_dict

    def read_csv_file(self):
        """Reads CSV file
        """
        csv_data = []
        with open(os.path.join(self.GROCERY_PATH, self.filename),
                  mode='r', encoding='latin1') as csv_file:
            csv_reader = csv.reader(csv_file, dialect='excel', delimiter=',',
                                    quoting=csv.QUOTE_ALL)
            for row in csv_reader:
                csv_data.append(row)
        csv_data = csv_data[1:]  # remove field name row
        self.set_csv_data(csv_data)

    def sort_csv_data(self):
        """Sorts CSV data
        """
        # Sort by grocery item
        temp1 = sorted(self.csv_data, key=operator.itemgetter(2))
        # Sort by date
        temp2 = sorted(temp1,
                       key=lambda d: datetime.strptime(d[1], "%d-%m-%Y"))
        # Sort by member number
        sorted_csv_data = sorted(temp2, key=operator.itemgetter(0))
        self.set_csv_data(sorted_csv_data)
