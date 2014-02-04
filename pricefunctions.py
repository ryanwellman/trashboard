"""
this module contains the functions that extract price tables from the database structure

XXX: needs db call optimization
"""
from itertools import chain
from json import dumps, loads
from datetime import datetime, timedelta
from django.utils import timezone
from agreement.models import *
from handy import uniq


def get_productprice_list(campaign):
    """
    get list of product prices and deduplicate it
    """

    # sort this dictionary by zorder highest first
    pts = get_zorders(campaign)
    sorted_pts = sorted(pts, key=lambda i: i.get('zorder'), reverse=True)

    # var scoping
    price_set = []

    # get all the productprices
    for obj in sorted_pts:
        pt = obj.get('pt')
        for pp in pt.productprice_set.all():
            # fix the date values from null
            fromdate = pp.fromdate or timezone.now() - timedelta(days=1)
            todate = pp.todate or timezone.now() + timedelta(days=1)
            # insert promo prices at the head of the line
            if pp.promo:
                price_set.insert(0, pp)
            # make sure this price is temporally accurate
            elif fromdate < timezone.now() < todate:
                price_set.append(pp)
            # keep going
            else:
                continue

    return uniq(price_set, key=lambda pp: pp.product.code)

def get_global_context(campaign):
    """
    generate the lists that go into the container view
    """

    # XXX: this function and its predecessors use too many queries

    # cache product price list
    pricelist = get_productprice_list(campaign)

    # variables
    parts, packages, closers, services, combos, premiums, incentives, monitors, shippers = ([], [], [], [], [], [], [], [], [])

    # get packages first
    for pack in Package.objects.all():
        # cache contents
        contents = []
        for pkgp in pack.pkgproduct_set.all():
            contents.append(dict(code=pkgp.product.code, quantity=pkgp.quantity))

        # add to packages
        packages.append(dict(code=pack.code, name=pack.name, contents=contents))

    # step through parts list and assign items to the variables we need
    # XXX: use product type here?
    for prod in pricelist:
        # prod is a productprice object and this allows things to get crazy
        # anything with a price table entry shows up here so we have to handle
        # every kind of product

        # premium items
        if prod.product.category == 'Premium Items':
            # get contents
            pitems = []
            for cline in ComboLine.objects.filter(parent=prod.product):
                pitems.append(dict(code=cline.product.code, quantity=cline.quantity))

            premiums.append(dict(code=prod.product.code, name=prod.product.name, price=format(prod.monthly_price or 0, '.2f'), description=prod.product.description, category=prod.product.category, contents=pitems))
        elif prod.product.category == 'Services':
            services.append(dict(code=prod.product.code, name=prod.product.name, price=format(prod.monthly_price or 0, '.2f'), reason=prod.product.description))
        elif prod.product.category == 'Rate Drops':
            closers.append(dict(code=prod.product.code, name=prod.product.name, description=prod.product.description))
        elif prod.product.category == 'Combos':
            # get contents
            citems = []
            for cline in ComboLine.objects.filter(parent=prod.product):
                citems.append(dict(code=cline.product.code, quantity=cline.quantity))

            combos.append(dict(code=prod.product.code, name=prod.product.name, price=format(prod.monthly_price or 0, '.2f'), description=prod.product.description, category=prod.product.category, contents=citems))
        elif prod.product.category == 'Incentives':
            incentives.append(dict(code=prod.product.code, name=prod.product.name, price=format(prod.monthly_price or 0, '.2f'), reason=prod.product.description))
        elif prod.product.category == 'Monitoring':
            monitors.append(dict(name=prod.product.name, value=prod.product.code))
        elif prod.product.category == 'Shipping':
            shippers.append(dict(name=prod.product.name, value=prod.product.code))
        else:
            # has not been appended elsewhere
            parts.append(dict(code=str(prod.product.code), name=str(prod.product.name), points=str(prod.cb_points), category=str(prod.product.category), price=format(prod.monthly_price or 0, '.2f')))

    # return something our view model can use as context
    return dict(parts=dumps(parts), packages=dumps(packages), closers=dumps(closers), services=dumps(services), combos=dumps(combos), premiums=dumps(premiums), incentives=dumps(incentives), monitors=dumps(monitors), shippers=dumps(shippers))
