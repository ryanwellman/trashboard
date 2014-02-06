#!/usr/bin/env python
"""
this program attempts to create the database entries required for trashboard to run
"""
# system imports
import sys, re

# std imports
from argparse import ArgumentParser
from datetime import datetime
from itertools import chain
from math import exp
from socket import gethostbyaddr
from time import time, sleep
from pprint import pprint as p

# my imports
import agreement.models

VERSION = '0.1 alpha'

def CreateDBEntries():
    """this thing calls all the others"""

    # price things
    CreatePriceGroups()
    CreatePriceTables()
    CreatePGMemberships()

    # business entity things
    CreateOrganizations()
    CreateCampaigns()

    # producty things
    CreateProducts()
    CreateProductContents()

    # actual price lists
    CreateProductPrices()


def CreatePriceGroups():
    """make all the price groups"""

    PriceGroup(name='Fake PG').save()
    PriceGroup(name='PG Thirteen').save() # lel


def CreatePriceTables():
    """make all the price tables"""

    PriceTable(name='Base').save()
    PriceTable(name='Overlay').save()


def CreatePGMemberships():
    """attach the price tables to price groups with this through table"""

    # obtain the pts
    base = PriceTable.objects.get(name='Base')
    overlay = PriceTable.objects.get(name='Overlay')

    # obtain the pgs
    fakepg = PriceGroup.objects.get(name='Fake PG')
    pgthirteen = PriceGroup.objects.get(name='PG Thirteen')

    PGMembership(pricegroup=fakepg, pricetable=overlay, notes='sxh wuz here', zorder=1, date_updated=datetime.now()).save()
    PGMembership(pricegroup=fakepg, pricetable=base, notes='sxh wuz here too', zorder=0, date_updated=datetime.now()).save()
    PGMembership(pricegroup=pgthirteen, pricetable=base, notes='totally real yo', zorder=0, date_updated=datetime.now()).save()


def CreateCampaigns():
    """make all the campaigns"""

    # obtain an organization
    test = Organization.objects.get(provider_id='TEST')

    # obtain a price group
    fakepg = PriceGroup.objects.get(name='Fake PG')

    Campaign(campaign_id='X00000', name='Test Campaign', pricegroup=fakepg, organization=test).save()


def CreateOrganizations():
    """make all the organizations"""

    # obtain a price group
    pgthirteen = PriceGroup.objects.get(name='PG Thirteen')

    Organization(provider_id='TEST', name='Test Organization', pricegroup=pgthirteen).save()


def CreateProducts():
    """make all the products by their child models"""

    Closer(code='10RTDROP', product_type='Closer', category='Rate Drops', name='$10/mo rate drop', description='Removes $10 per month (requires manager approval)').save()
    Closer(code='5RTDROP', product_type='Closer', category='Rate Drops', name='$5/mo rate drop', description='Removes $5 from the monthly monitoring').save()
    Closer(code='FREEKEY', product_type='Closer', category='Rate Drops', name='Free Keychains', description='Give away some of our famous disposable keychains!').save()
    Closer(code='FREESHIP', product_type='Closer', category='Rate Drops', name='Free Shipping', description='Cancels out shipping cost for the customer').save()

    Part(code='ANTENNA', product_type='Part', category='Premium Items', name='Cellular Antenna', description='Cut the wires and it still works!').save()
    Part(code='CRBMDT', product_type='Part', category='Fire Sensors', name='Carbon Monoxide detector', description='').save()
    Part(code='DWSENS', product_type='Part', category='Window Sensors', name='Door/Window Sensors', description='').save()
    Part(code='FLSENS', product_type='Part', category='Security Sensors', name='Flood Sensor', description='').save()
    Part(code='GBSENS', product_type='Part', category='Security Sensors', name='Glass Break Sensor', description='').save()
    Part(code='GDSENS', product_type='Part', category='Security Sensors', name='Garage Door Sensor', description='').save()
    Part(code='KEYCRC', product_type='Part', category='Accessories', name='Keychain Remote Control', description='').save()
    Part(code='LTSENS', product_type='Part', category='Security Sensors', name='Low Temperature Sensor', description='').save()
    Part(code='MEDPEN', product_type='Part', category='Accessories', name='Medical Panic Pendant', description='').save()
    Part(code='MEDPNB', product_type='Part', category='Accessories', name='Medical Panic Bracelet', description='').save()
    Part(code='MINPNP', product_type='Part', category='Accessories', name='Mini Pinpad', description='').save()
    Part(code='MOTDEC', product_type='Part', category='Security Sensors', name='Motion Detector', description='').save()
    Part(code='SIMNXT', product_type='Part', category='Security Panels', name='Simon XT', description='').save()
    Part(code='SIMTHR', product_type='Part', category='Security Panels', name='Simon 3', description='').save()
    Part(code='SMKDET', product_type='Part', category='Fire Sensors', name='Smoke Detector', description='').save()
    Part(code='SOLLGT', product_type='Part', category='Accessories', name='Solar Light', description='').save()
    Part(code='TLKDEV', product_type='Part', category='Security Panels', name='Talkover Device', description='').save()
    Part(code='TLKKYP', product_type='Part', category='Accessories', name='Talking Keypad', description='').save()
    Part(code='TLKTSC', product_type='Part', category='Accessories', name='XT Talking Touchscreen', description='').save()
    Part(code='XTNAPM', product_type='Part', category='Home Automation', name='X10 Appliance Module', description='').save()
    Part(code='XTNSIR', product_type='Part', category='Home Automation', name='XT Siren', description='').save()
    Part(code='XTSRCK', product_type='Part', category='Home Automation', name='X10 Socket Rocket', description='').save()

    Service(code='ALPACASRV', product_type='Service', category='Services', name='Alpaca Rental Service', description='You bought alpaca shears and now need an alpaca').save()
    Service(code='SMOKESRV', product_type='Service', category='Services', name='Smoke Service', description='You bought a smoke detector and now need this').save()
    Service(code='VIDEOSRV', product_type='Service', category='Services', name='Video Service', description='You got a camera and now need this').save()

    Combo(code='COMBOTEST', product_type='Combo', category='Combos', name='Test Combo', description='so combo wow much products').save()

    Monitoring(code='BROADBAND', product_type='Monitoring', category='Connection Method', name='', description='Broadband monitoring').save()
    Monitoring(code='LANDLINE', product_type='Monitoring', category='Connection Method', name='', description='Landline monitoring').save()
    Monitoring(code='CELLULAR', product_type='Monitoring', category='Connection Method', name='', description='Cellular monitoring').save()

    Shipping(code='UPS', product_type='Shipping', category='Shipping Method', name='UPS Ground', description='2-3 business days').save()
    Shipping(code='FEDEX', product_type='Shipping', category='Shipping Method', name='FedEx Regular', description='3-5 business days').save()
    Shipping(code='USPS', product_type='Shipping', category='Shipping Method', name='USPS Priority Mail', description='allegedly 2-3 business days, maybe not').save()
    Shipping(code='JPOST', product_type='Shipping', category='Shipping Method', name='Japan Post EMS', description='overnight').save()

    Package(code='COPPER', product_type='Package', category='Packages', name='Copper', description='Copper package').save()
    Package(code='BRONZE', product_type='Package', category='Packages', name='Bronze', description='Bronze package').save()
    Package(code='SILVER', product_type='Package', category='Packages', name='Silver', description='Silver package').save()
    Package(code='GOLD', product_type='Package', category='Packages', name='Gold', description='Gold package').save()
    Package(code='PLATINUM', product_type='Package', category='Packages', name='Platinum', description='Platinum package').save()
    Package(code='BUSINESS', product_type='Package', category='Packages', name='Business', description='Business package').save()


def CreateProductContents():
    """add contents to those products that require it"""

    # stuff we put in all packages
    dwsens = Part.objects.get(code='DWSENS')
    simnxt = Part.objects.get(code='SIMNXT')
    motdec = Part.objects.get(code='MOTDEC')


    # how many dwsens are in each package
    dwsens_qtys =  {
                'COPPER': 3,
                'BRONZE': 7,
                'SILVER': 10,
                'GOLD': 12,
                'PLATINUM': 15,
                'BUSINESS': 20,
            }

    # put these things in the packages with fake upfront strike prices
    for k, v in dwsens_qtys.iteritems():
        current_package = Package.objects.get(code=k)
        ProductContent(included_in=current_package, included_product=dwsens, quantity=v, upfront_strike=5.0, monthly_strike=None).save()
        ProductContent(included_in=current_package, included_product=simnxt, quantity=1, upfront_strike=5.0, monthly_strike=None).save()
        ProductContent(included_in=current_package, included_product=motdec, quantity=2, upfront_strike=5.0, monthly_strike=None).save()

    # stuff that goes in combos
    gdsens = Part.objects.get(code='GDSENS')

    # combos
    testcombo = Combo.objects.get(code='COMBOTEST')

    # put stuff in the combos with fake upfront strike prices
    ProductContent(included_in=testcombo, included_product=gdsens, quantity=2, upfront_strike=5.5, monthly_strike=None).save()

    # stuff that goes in closers



def CreateProductPrices():
    """give prices to products on price tables without which they would not exist"""

    # obtain the pts
    base = PriceTable.objects.get(name='Base')
    overlay = PriceTable.objects.get(name='Overlay')

    # XXX: these prices are fake
    # assign upfront prices to parts and give them certain other identical attributes
    for part in Part.objects.all():
        ProductPrice(pricetable=base, product=part, max_quantity=99, monthly_price=None, upfront_price=6.0, cb_points=5, fromdate=None, todate=None, promo=False, swappable=True).save()

    # now assign a fake, but different upfront pp to the dwsens part on the overlay pricetable
    ProductPrice(pricetable=overlay, product=Part.objects.get(code='DWSENS'), max_quantity=99, monthly_price=None, upfront_price=4.0, cb_points=None, fromdate=None, todate=None, promo=False, swappable=True).save()

    # do the same thing for the combo products
    for combo in Combo.objects.all():
        ProductPrice(pricetable=base, product=combo, max_quantity=99, monthly_price=None, upfront_price=7.0, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

    # monitoring and services are both rmr things so we will do them together
    for rmr_thing in chain(Monitoring.objects.all(), Service.objects.all()):
        ProductPrice(pricetable=base, product=rmr_thing, max_quantity=1, monthly_price=8.0, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

    # now let's do the packages which have both kinds of prices
    for package in Package.objects.all():
        ProductPrice(pricetable=base, product=package, max_quantity=1, monthly_price=8.5, upfront_price=10.0, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

    # these don't really have a price at all
    for shipping in Shipping.objects.all():
        ProductPrice(pricetable=base, product=shipping, max_quantity=1, monthly_price=None, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

    # these closers are free so they have no prices
    for closer in Closer.objects.filter(code__in=['FREEKEY', 'FREESHIP']):
        ProductPrice(pricetable=base, product=closer, max_quantity=1, monthly_price=None, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

    # now fix the other two to have negative prices
    ProductPrice(pricetable=base, product=Closer.objects.get(code='10RTDROP'), max_quantity=1, monthly_price=-10.0, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()
    ProductPrice(pricetable=base, product=Closer.objects.get(code='5RTDROP'), max_quantity=1, monthly_price=-5.0, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

def MainLoop():
    """handles the execution of this program"""

    # set up an argument parser
    parser = ArgumentParser(description='a fake fixture for django models that inherit from other models', epilog='under construction')
    parser.add_argument('-v', '--version', action='version', version='\033[94m%(prog)s\033[0m v' + VERSION)

    # obtain command line arguments
    args = parser.parse_args()

    # advertise to stdout
    print '\033[94m' + sys.argv[0] + '\033[0m'

    CreateDBEntries()

if __name__ == '__main__':
    MainLoop()