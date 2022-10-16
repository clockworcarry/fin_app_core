import moka as moka
import datetime as datetime

""" PyBind notes

- Missing attribute in object: attribute error exception thrown
- casting attribute wrong type (ex: try to cast int attr to str: runtime error thrown)

"""

class CompanyGrowthParam:
    def __init__(self):
        self.metric_code = ''
        self.nb_quarters_back = 0
        self.nb_yrs_back = 0
        self.date_start = None
        self.date_end = None

def test_log_exceptions_to_db():
    param_one = CompanyGrowthParam()
    param_one.metric_code = 'ps'
    param_one.nb_quarters_back = 1

    param_two = CompanyGrowthParam()
    param_two.metric_code = 'pe'
    param_two.nb_yrs_back = 5

    param_three = CompanyGrowthParam()
    param_three.metric_code = 'roe'
    param_three.date_start = datetime.datetime(2021, 5, 20)
    param_three.date_start = datetime.datetime(2022, 6, 15)

    param_four = CompanyGrowthParam()
    param_four.metric_code = 'fcf'
    param_four.nb_quarters_back = None
    param_four.nb_yrs_back = None
    param_four.date_start = None
    param_four.date_end = None

    l = [param_one, param_two, param_three, param_four]

    screener = moka.EquityScreener(l)
    
    
