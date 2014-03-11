from decimal import Decimal
from datetime import date

# I hate that I'm doing this.
'''
TAX_MAP = {
    'AL': (Decimal('0.1'), False, True),
    'GA': (Decimal('0.07'), False, True),
    'LA': (Decimal('0.09'), False, True),
    'NC': (Decimal('0.07'), False, True),
    'SC': (Decimal('0.06'), False, True),
    'AR': (Decimal('0.085'), True, True),
    'FL': (Decimal('0.07'), True, True),
    'MS': (Decimal('0.07'), True, True),
    'NM': (Decimal('0.05125'), True, True),
    'TX': (Decimal('0.0825'), True, True),
    'WV': (Decimal('0.06'), True, True),

    # Canadian tax rates
    'AB': (Decimal('0.05'), True, True),
    'BC': (Decimal('0.12'), True, True),
    'ON': (Decimal('0.13'), True, True),
}
'''

class TaxData(object):
    def __init__(self, rate, sales, service, from_date, to_date):
        self.rate = rate
        self.sales = sales
        self.service = service
        self.from_date = from_date
        self.to_date = to_date

    def as_tuple(self):
        return (self.rate, self.service, self.sales)

NEW_TAX_MAP = {
    #Canada
    'ON': [
        TaxData(sales=True, rate=Decimal('0.13'), service=True, from_date=None, to_date=None),
    ],
    'BC': [
        TaxData(sales=True, rate=Decimal('0.12'), service=True, from_date=None, to_date=None),
    ],
    'AB': [
        TaxData(sales=True, rate=Decimal('0.05'), service=True, from_date=None, to_date=None),
    ],


    'NM': [
        TaxData(sales=True, rate=Decimal('0.05125'), service=True, from_date=None, to_date=None),
    ],
    'TX': [
        TaxData(sales=True, rate=Decimal('0.0825'), service=True, from_date=None, to_date=None),
    ],
    'MS': [
        TaxData(sales=True, rate=Decimal('0.07'), service=True, from_date=None, to_date=None),
    ],
    'NC': [
        TaxData(sales=True, rate=Decimal('0.07'), service=False, from_date=None, to_date=None),
    ],
    'LA': [
        TaxData(sales=True, rate=Decimal('0.09'), service=False, from_date=None, to_date=None),
    ],
    'AL': [
        TaxData(sales=True, rate=Decimal('0.1'), service=False, from_date=None, to_date=None),
    ],
    'WV': [
        TaxData(sales=True, rate=Decimal('0.06'), service=True, from_date=None, to_date=None),
    ],
    'AR': [
        TaxData(sales=True, rate=Decimal('0.085'), service=True, from_date=None, to_date=date(2013,9,1)),
        TaxData(sales=True, rate=Decimal('0.090'), service=True, from_date=date(2013,9,1), to_date=None),
    ],
    'GA': [
        TaxData(sales=True, rate=Decimal('0.07'), service=False, from_date=None, to_date=date(2013,7,1)),
        TaxData(sales=True, rate=Decimal('0.08'), service=False, from_date=date(2013,7,1), to_date=None),
    ],
    'SC': [
        TaxData(sales=True, rate=Decimal('0.06'), service=False, from_date=None, to_date=None),
    ],
    'FL': [
        TaxData(sales=True, rate=Decimal('0.07'), service=True, from_date=None, to_date=None),
    ],
}

def get_tax_object(state, *dates):
    # Fetch the first non-null date
    dates = filter(None, dates)
    if not dates:
        raise Exception('No valid dates provided to get_tax_object')

    d = dates[0]
    ranges = NEW_TAX_MAP.get(state.upper(), [])

    for r in ranges:
        if (r.from_date is None or d.date() >= r.from_date) and (r.to_date is None or d.date() < r.to_date):
            return r

    return None

def get_tax(state, *dates):
    """
    BAA 2013-07-01: This function now requires the effective tax date in order
                     to return the correct tax rate at that time.

    Returns None if the state is not taxed. Otherwise, returns a three-tuple
    of the form: (tax rate, tax_monitoring, tax_equipment). Tax rate is a
    Decimal object, the other two fields are booleans that indicate if that
    specific item type is taxed.

    Monitoring tax includes all services, tech installs, and addenda
    Equipment tax covers all equipment costs and shipping
    """


    tax_obj = get_tax_object(state, *dates)
    if not tax_obj:
        return None

    return tax_obj.as_tuple()

