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

BET_WAIT_TIME = 1200


'''
Prikaz v tvare:
(kazdy argument na novom riadku)
$bet
sport (vsetkos malym)
timA|timB {alebo} timA {alebo} timB  (len jedna z tychto moznosti (1. preferrable pre peknost reportu))
kolonka v krotrej stavit  (pri fortune napriklad 'Zápas: počet gólov')
konkretna stavka v kolonke (napr: 'Menej ako (2.5)' pri fortune dodrzat presny format (1. pismeno velke))
'''

