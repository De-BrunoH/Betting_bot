from betting.broker_ifortuna import IFortuna


ACCOUNTS_IFORTUNA = [
    {'name': 'Brunis', 'password': 'Sigmabet123', 'bet_amount': 100}
]

ACCOUNTS_DOXXBET = []

BROKERS = {
    'IFortuna': (IFortuna(), ACCOUNTS_IFORTUNA)
}

# ======================
# COMMAND PARTS
# ----------------------
# 0
ALLOWED_SPORTS = {
    'futbal'
}

# 1
# Events, that is upto sender to get it right

# 2
ALLOWED_BETS_PER_SPORT = {
    'futbal': {'Zápas: počet gólov'}
}

