from itertools import combinations


class PreController:
    """Responsible for creating transactions list from CSV data
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def run(self):
        self.model.set_constraints(self.view.prompt_constraints())
        self.model.read_csv_file()
        self.model.sort_csv_data()
        self.create_trans()
        self.view.write_csv('1_trans.csv', self.model.trans)

    def create_trans(self):
        """Creates and returns trimmed transactions list, 3 steps
        1) Takes CSV data and squishes it into a unfiltered transactions list
        2) Takes unfiltered transactions and removes duplicate items
        3) Filters unnecessary fields and returns transactions list
        """
        unfiltered_trans = []
        curr_trans = self.model.csv_data[0]
        for i in range(0, len(self.model.csv_data)):
            csv_number = self.model.csv_data[i][0]  # member number
            csv_date = self.model.csv_data[i][1]
            csv_item = self.model.csv_data[i][2]
            trans_number = curr_trans[0]
            trans_date = curr_trans[1]
            # member id or date are different
            if (trans_number != csv_number) or (trans_date != csv_date):
                num_items = len(curr_trans) - 2
                curr_trans.insert(2, str(num_items))
                unfiltered_trans.append(curr_trans)
                curr_trans = [csv_number, csv_date, csv_item]
            # member id and date are same
            else:
                curr_trans.append(csv_item)
        num_items = len(curr_trans) - 2
        curr_trans.insert(2, str(num_items))
        unfiltered_trans.append(curr_trans)
        # eg [ ['1702','12-01-2014','3','pip fruit','yogurt,'yogurt'], ... ]

        filtered_trans = []
        for trans in unfiltered_trans:
            itemset = list(set(trans[3:]))  # remove duplicates
            # sort again (becomes unordered for some reason)
            itemset = sorted(itemset)
            new_trans = trans[:3]
            new_trans.extend(itemset)
            # set num items in itemset
            new_trans[2] = len(new_trans) - 3
            filtered_trans.append(new_trans)
        # eg [ ['1702','12-01-2014','2','pip fruit','yogurt], ... ]

        trimmed_trans = []
        for a_trans in filtered_trans:
            trimmed_trans.append(a_trans[3:])
        # eg [ ['pip fruit','yogurt'], ... ]
        self.model.set_trans(trimmed_trans)


class EclatController:
    """Responsible for finding frequent itemsets using ECLAT algorithm
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def run(self):
        self.create_item_tidset_dict()
        self.view.write_csv('2a_item_tidset.csv', self.model.item_tidset_dict)
        self.create_itemset_tidset_dict()
        self.view.write_csv('2b_itemset_tidset.csv',
                            self.model.itemset_tidset_dict)
        self.view.write_frequency('2c_frequency.csv',
                                  self.model.itemset_tidset_dict)

    def create_item_tidset_dict(self):
        """Creates item to tidset dict
        eg { 'soda': {2, 6, ...}, ... }
        """
        item_tidset_dict = dict()
        for tid in range(0, len(self.model.trans)):
            an_itemset = self.model.trans[tid]
            for i in range(0, len(an_itemset)):
                item = an_itemset[i]
                if item not in item_tidset_dict:
                    item_tidset_dict[item] = {tid}
                else:  # add onto existing key
                    item_tidset_dict[item].add(tid)
        self.model.set_item_tidset_dict(item_tidset_dict)

    def create_itemset_tidset_dict(self):
        """Creates itemset to tidset dict
        eg { 'pastry': {0, 4096, ...} ... ,
            ('pastry', 'whole milk'): {0, 4096 ...} }
        """
        # Hold only one k-length itemset, temporarily
        k_itemset_tidset = self.model.item_tidset_dict.copy()
        # Will hold all k-length itemsets
        full_itemset_tidset = dict()
        k = 2

        while len(k_itemset_tidset) != 0:
            # Filter entries below minimum support
            k_itemset_tidset = dict(
                filter(
                    lambda entry: len(entry[1]) >= self.model.min_supp,
                    k_itemset_tidset.items()
                )
            )
            # Add k_itemset_tidset to return list
            full_itemset_tidset.update(k_itemset_tidset)
            # Create all poss k itemset combinations
            combs = self.find_combs(k, k_itemset_tidset)
            # Generate next k_itemset_tidset from combinations
            k_itemset_tidset = self.find_k_itemset_tidset_dict(combs)
            k += 1
        self.model.set_itemset_tidset_dict(full_itemset_tidset)

    def find_combs(self, k, k_itemset_tidset):
        """Finds k-length combinations from k-length itemsets
        eg [ ('item1', 'item2'), ...]
        """
        if k == 2:
            items_list = list(k_itemset_tidset.keys())
        else:
            items_list = set()  # set ensures no repeat items
            for itemset in k_itemset_tidset.keys():
                for item in itemset:
                    items_list.add(item)
            items_list = list(items_list)
        combs = list(combinations(items_list, k))
        return combs

    def find_k_itemset_tidset_dict(self, combs):
        """Creates k-length itemset tidset dictionary from k-length
        combinations list
        """
        k_itemset_tidset_dict = dict()
        for a_comb in combs:
            item0 = a_comb[0]  # first combination
            # initialize tidset with first tidset
            tidset_intersect = self.model.item_tidset_dict[item0]
            for i in range(1, len(a_comb)):
                next_item = a_comb[i]
                next_tidset = self.model.item_tidset_dict[next_item]
                tidset_intersect = tidset_intersect.intersection(next_tidset)
            if len(tidset_intersect) >= self.model.min_supp:
                k_itemset_tidset_dict[a_comb] = tidset_intersect
        return k_itemset_tidset_dict


class RuleController:
    """Responsible for association rule generation from frequent itemsets
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def run(self):
        self.create_itemset_rule_dict()
        self.view.write_csv('3a_itemset_rule.csv',
                            self.model.itemset_rule_dict)
        self.create_rule_stat_dict()
        self.view.write_rule_stat('3b_rule_stat.csv',
                                  self.model.rule_stat_dict)

    def create_itemset_rule_dict(self):
        """Create association rules from frequent itemsets
        eg {('ham', 'whole milk'):
            [({'ham'}, {'whole milk'}), ({'whole milk'}, {'ham'}), ...], ... }
        """
        itemset_rule_dict = dict()
        for itemset, tidset in self.model.itemset_tidset_dict.items():
            # 1-itemsets are str type, 2+ itemsets are tuples
            if type(itemset) is tuple:
                rule_list = []
                for i in range(1, len(itemset)):
                    combs_list = list(combinations(itemset, i))
                    for j in range(0, len(combs_list)):
                        antecedent = set(combs_list[j])
                        # Itemset can be thought of set(A) + set(C)
                        # So we can use some set math to isolate consequent
                        consequent = set(itemset) - antecedent
                        rule = (antecedent, consequent)
                        rule_list.append(rule)
                itemset_rule_dict[itemset] = rule_list
        self.model.set_itemset_rule_dict(itemset_rule_dict)

    def create_rule_stat_dict(self):
        """Creates support, confidence, lift from association rules
        eg {(('frankfurter'), ('other vegetables')):
            (0.0051, 0.1363, 1.1163), ...}
        """
        rule_stat = dict()

        for itemset, assoc_rules in self.model.itemset_rule_dict.items():
            for rule in assoc_rules:
                ante = rule[0]
                cons = rule[1]
                ante_tidset = self.find_intersect(ante)
                cons_tidset = self.find_intersect(cons)
                joined_tidset = ante_tidset.intersection(cons_tidset)
                num_ante = len(ante_tidset)
                num_cons = len(cons_tidset)
                num_joined = len(joined_tidset)
                supp = num_joined / len(self.model.trans)
                conf = num_joined / num_ante
                lift = conf / (num_cons / len(self.model.trans))
                if conf >= self.model.min_conf and lift >= self.model.min_lift:
                    supp = round(supp, 6)
                    conf = round(conf, 4)
                    lift = round(lift, 4)
                    rule_stat[(tuple(ante), tuple(cons))] = (supp, conf, lift)
        self.model.set_rule_stat_dict(rule_stat)

    def find_intersect(self, itemset):
        """Finds tidset where itemset can be found in all tids
        """
        inter_tidset = set()
        for item in itemset:
            tidset = self.model.item_tidset_dict[item]
            if len(inter_tidset) == 0:  # can't intersect without something
                inter_tidset = inter_tidset.union(tidset)
            else:  # we have at least 1 tidset added, now we can intersect
                inter_tidset = inter_tidset.intersection(tidset)
        return inter_tidset
