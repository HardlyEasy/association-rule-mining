import time

from src.Controller import PreController, EclatController, RuleController
from src.Model import Model
from src.View import View


def main():
    """1) PreController: process CSV data into transactions list
    2) EclatController: find frequent itemsets from transactions
    3) RuleController: find association rules using frequent itemsets
    """
    model = Model()
    view = View()
    pre_controller = PreController(model, view)
    eclat_controller = EclatController(model, view)
    rule_controller = RuleController(model, view)

    pre_controller.run()
    start = time.time()
    eclat_controller.run()
    end = time.time()
    print(round(end - start, 2), 'seconds for eclat')
    rule_controller.run()
    print('End of program.')


if __name__ == '__main__':
    main()
