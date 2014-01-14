"""
this module contains the functions that extract price tables from the database structure

XXX: needs db call optimization
"""
from itertools import chain
from json import dumps, loads
from datetime import datetime, timedelta
from django.utils import timezone
from agreement.models import *

def uniqifier(seq):
    # uniqifier from peterbe.com/plog/uniqifiers-benchmark
    # alleges to preserve order and works based off of productprice codes
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x.product.code not in seen and not seen_add(x.product.code)]

def find_campaign_by_id(campaign_id):
    """
    get a campaign by its id
    """

    # relies on each id having only one campaign
    campaign = Campaign.objects.get(pk=campaign_id)
    return campaign

def find_parent_orgs(campaign):
    """
    figure out what a given campaign's parent organizations are
    """

    # return list of orgs
    found = []

    # loop over through tables
    for oc in campaign.orgcampaign_set.all():
        found.append(oc.organization)

    return found

def get_zorders(campaign):
    """
    get zorders for a given campaign
    """

    # obtain orgs
    organizations = find_parent_orgs(campaign=campaign)

    # var scoping
    z_list = []

    # obtain the price group first, campaign ones dominate
    if campaign.pricegroup:
        pricegroup = campaign.pricegroup
    else:
        # use the list here once to calculate the price group
        for org in organizations:
            z_list.append(dict(pg=org.pricegroup, zorder=org.zorder))

        # sort this list and take the top item
        z_sort = sorted(z_list, key=lambda i: i.get('zorder'), reverse=True)
        pricegroup = z_sort[0].pricegroup

    # search for the price table objects in the price group through table and obtain the zorders
    z_list = [] # clear
    for pt in PGMembership.objects.filter(pricegroup=pricegroup):
        z_list.append(dict(pt=pt.pricetable, zorder=pt.zorder))

    # return a list of dictionaries
    return z_list

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

    # deduplicate with a slightly modified f7 uniqifier
    return uniqifier(price_set)

def gen_arrays(campaign):
    """
    generate the lists that go into the container view
    """

    # XXX: this function and its predecessors use too many queries

    # cache product price list
    pricelist = get_productprice_list(campaign)

    # variables
    parts, packages, closers, services, combos, premiums, incentives = ([], [], [], [], [], [], [])

    # get packages first
    for pack in Package.objects.all():
        if pack.code=='blank':
            continue

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
        else:
            # has not been appended elsewhere
            parts.append(dict(code=str(prod.product.code), name=str(prod.product.name), points=str(prod.cb_points), category=str(prod.product.category), price=format(prod.monthly_price or 0, '.2f')))

    # return something our view model can use as context
    return dict(parts=dumps(parts), packages=dumps(packages), closers=dumps(closers), services=dumps(services), combos=dumps(combos), premiums=dumps(premiums), incentives=dumps(incentives))
