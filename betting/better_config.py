import betting.broker_ifortuna as fortuna


BROKERS = {
    'IFortuna': (fortuna.IFortuna(), {'name': 'Brunis', 'password': 'Sigmabet123', 'bet_amount': '100'})
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

TEST_COMMAND = {

}

