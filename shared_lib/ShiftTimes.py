#from pylab import *
from numpy import copy
#from numpy import *
from datetime import datetime, time, timedelta

def ShiftCorrection(ShiftDts, date):
    date_original = copy(date)      # copia de las fechas originales
    IDs = map(int, ShiftDts.keys())
    for i in IDs:
        str     = '%d' % i
        date[i] = date[i] + ShiftDts[str]
    #return -1
    out = {
        'dates_original': date_original,    # dates input
        'dates_shifted':  date              # dates shifted
    }
    return out

ShiftDts = {
    '31' : timedelta(hours=-1, minutes=+0),
    '34' : timedelta(hours=-1, minutes=+0), 
    '38' : timedelta(hours=+0, minutes=-30),
    '40' : timedelta(hours=+0, minutes=-45),
    '42' : timedelta(hours=-1, minutes=+0),
    '51' : timedelta(hours=-1, minutes=-15),
    '54' : timedelta(hours=+0, minutes=-30),
    '55' : timedelta(hours=+0, minutes=-50), 
    '58' : timedelta(hours=+0, minutes=-30),
    '68' : timedelta(hours=+0, minutes=-40),
    '71' : timedelta(hours=+0, minutes=-45),
    '83' : timedelta(hours=-1, minutes=+0),
    '86' : timedelta(hours=-1, minutes=+0),
    '97' : timedelta(hours=+0, minutes=-40),
    '99' : timedelta(hours=-1, minutes=+0),
    '118': timedelta(hours=+0, minutes=-40),
    '120': timedelta(hours=-1, minutes=+0),
    '124': timedelta(hours=+0, minutes=-30),
    '125': timedelta(hours=+0, minutes=-20),
    '129': timedelta(hours=+0, minutes=-50),
    '131': timedelta(hours=+0, minutes=-40),
    '134': timedelta(hours=-1, minutes=+0),
    '135': timedelta(hours=+0, minutes=-45),
    '137': timedelta(hours=+0, minutes=-45),
    '138': timedelta(hours=+0, minutes=-50),
    '139': timedelta(hours=+0, minutes=-35),
    '153': timedelta(hours=+0, minutes=-40),
    '155': timedelta(hours=+0, minutes=-30),
    '159': timedelta(hours=+0, minutes=-30),
    '160': timedelta(hours=+0, minutes=-30),
    '165': timedelta(hours=+0, minutes=-45),
    '168': timedelta(hours=-1, minutes=+0),
    '187': timedelta(hours=-1, minutes=+0),
    '191': timedelta(hours=-1, minutes=-15),
    '195': timedelta(hours=-1, minutes=+0),
    '197': timedelta(hours=+0, minutes=-45),
    '199': timedelta(hours=+0, minutes=-45),
    '200': timedelta(hours=+0, minutes=-30),
    '203': timedelta(hours=+0, minutes=-40),
    '207': timedelta(hours=+0, minutes=-50),
    '208': timedelta(hours=+0, minutes=-50),
    '215': timedelta(hours=-1, minutes=+0),
    '223': timedelta(hours=+0, minutes=-25),
    '229': timedelta(hours=-1, minutes=+0),
    '233': timedelta(hours=+0, minutes=-40),
    '241': timedelta(hours=+0, minutes=-35),
    '246': timedelta(hours=-1, minutes=+0),
    '250': timedelta(hours=+0, minutes=-45),
    '251': timedelta(hours=+0, minutes=-35),
    '253': timedelta(hours=+0, minutes=-25),
    '255': timedelta(hours=+0, minutes=-50),
    '258': timedelta(hours=+0, minutes=-30),
    '272': timedelta(hours=+0, minutes=-30),
    '273': timedelta(hours=-1, minutes=+0),
    '277': timedelta(hours=-1, minutes=+0),
    '278': timedelta(hours=+0, minutes=-45),
    '281': timedelta(hours=-1, minutes=+0),
    '292': timedelta(hours=-1, minutes=+0),
    '293': timedelta(hours=+0, minutes=-40),
    '294': timedelta(hours=-1, minutes=+0),
    '299': timedelta(hours=+0, minutes=-45),
    '300': timedelta(hours=-1, minutes=-15),
    '304': timedelta(hours=+0, minutes=-25)
    }
#EOF
