


"""
Global constants
"""

ROOT = 'c:/dawa/stockassist'
MONTHS = 12
THRESHOLD_SCORE = 0.4

MARKET='nasdaq'
MARKET_PAGE_TOTAL = 16
MARKETDATA_SYMBOL = '^NDX'

# MARKET = 'ftse'
# MARKET_PAGE_TOTAL = 32
# MARKETDATA_SYMBOL = '^FTSE'


RELOAD_MISSING_DATA = False
TRACE = True

""""
Helper Functions
"""
def Print(statement):
    if TRACE:
        print(statement)


def confirm_choice():
    confirm = input("[c]Confirm or [v]Void: ")
    if confirm != 'c' and confirm != 'v':
        print("Invalid option. Please Enter a Valid Option.")
        return confirm_choice()
    print(confirm)
    return confirm


if __name__ == "__main__":
    print("***Global Constants***")
    print("ROOT: {}".format(ROOT))
    print(" MARKET: {}".format(MARKET))
    print(" MARKET_PAGE_TOTAL: {}".format(MARKET_PAGE_TOTAL))