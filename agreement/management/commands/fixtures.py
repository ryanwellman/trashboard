"""
this program attempts to create the database entries required for trashboard to run
"""

# std imports
from datetime import datetime
from time import time
from decimal import Decimal

# django imports
from django.core.management.base import BaseCommand, CommandError

# my imports
from agreement.models import *
from inventory.models import *
from org.models import *


NAME = 'fixtures'
VERSION = '0.3 alpha'

PRICETABLES =   {
                    #7:
                    'saveology:2014-03-18': {'WSMOKE': ('PART', '125.00', Decimal('149.99'), 'N/A', Decimal('0.00'), 1L, '75', 'Smoke Detector', 'FIRE'), 'GOLD': ('PACKAGE', 'N/A',Decimal('0.00'), '0.00', Decimal('39.99'), 0L, 'N/A', 'Gold', 'PACKAGE'), 'ZLKTS': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '260', 'Z-Wave Touchscreen Lock - Satin Nickel', 'HOMEAUTO'), 'ZLKTO': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '260', 'Z-Wave Touchscreen Lock - Oil Rubbed Bronze', 'HOMEAUTO'), '2TP': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '65', 'Talking Wireless Keypad', 'ACCESSORY'), 'VIDEOSERVICE': ('PART', '0.00', Decimal('0.00'), 'N/A', Decimal('5.00'), 0L, '0', 'Additional Video Service', 'VIDEO'), 'RKT': ('PART', '79.00', Decimal('99.99'), 'N/A', Decimal('0.00'), 1L, '45', 'X10 Socket Rocket', 'HOMEAUTO'), 'DGSKT': ('PART', '15.00', Decimal('15.00'), 'N/A', Decimal('0.00'), 1L, '15', 'Yale Lock Thin Door Gasket', 'HOMEAUTO'), 'XT-2WTTS': ('PART', '115.00', Decimal('115.00'), 'N/A', Decimal('0.00'), 1L, '65', 'Simon XT Touch Screen Keypad', 'ACCESSORY'), 'CAMERA': ('PART', '199.00', Decimal('249.99'), 'N/A', Decimal('0.00'), 0L, '125', 'Video Camera', 'VIDEO'), 'ZLKTB': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '260', 'Z-Wave Touchscreen Lock - Polished Brass', 'HOMEAUTO'), 'SECRETKEYPAD': ('PART', '49.00', Decimal('69.99'), 'N/A', Decimal('0.00'), 1L, '20', 'Secret Keypad', 'ACCESSORY'), 'WPANIC': ('PART', '95.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '60', 'Medical Panic Pendant', 'ACCESSORY'), 'TWOWAY': ('MONITORING', 'N/A', Decimal('59.00'), '357.00', Decimal('5.00'), 0L, 'N/A', 'Two-Way Voice', 'MONITORING'), 'OVERNIGHT': ('SHIPPING', 'N/A', Decimal('49.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Overnight Shipping', 'SHIPPING'), 'WGLASS': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '65', 'Glass Break Detector', 'SENSOR'), 'UTA': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('10.00'), 0L, '50', 'GPS Tracking Device', 'GPS'), 'BROADBAND': ('MONITORING', 'N/A', Decimal('89.00'), '387.00', Decimal('7.00'), 0L, 'N/A', 'Broadband', 'MONITORING'), 'SIMONXT': ('PART', '299.00', Decimal('399.00'), 'N/A', Decimal('0.00'), 0L, '125', 'Simon XT Control Panel', 'PANEL'), 'FREEZE': ('PART', '125.00', Decimal('149.99'), 'N/A', Decimal('0.00'), 1L, '50', 'Freeze Sensor', 'SENSOR'), 'FLOOD': ('PART', '125.00', Decimal('149.99'), 'N/A', Decimal('0.00'), 1L, '60', 'Flood Sensor', 'SENSOR'), 'CELLULAR': ('MONITORING', 'N/A', Decimal('139.00'), '536.00', Decimal('12.00'), 0L, 'N/A', 'Cellular', 'MONITORING'), 'WCONT': ('PART', '39.50', Decimal('49.99'), 'N/A', Decimal('0.00'), 1L, '25', 'Micro Door/Window Sensor', 'SENSOR'), 'STANDARD': ('MONITORING', 'N/A', Decimal('40.00'), '239.00', Decimal('0.00'), 0L, 'N/A', 'Standard', 'MONITORING'), '4KEY': ('PART', '49.50', Decimal('69.99'), 'N/A', Decimal('0.00'), 1L, '25', '4-Button Keychain Remote Control', 'ACCESSORY'), 'GROUND': ('SHIPPING', 'N/A',Decimal('19.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Ground Shipping', 'SHIPPING'), 'SIMON3': ('PART', '299.00', Decimal('350.00'), 'N/A', Decimal('0.00'), 0L, '125', 'Simon 3', 'PANEL'), 'GARAGE': ('PART', '79.00', Decimal('99.99'), 'N/A', Decimal('0.00'), 1L, '40', 'Overhead Garage Door Sensor', 'SENSOR'), 'LAMP': ('PART', '79.00', Decimal('99.99'), 'N/A', Decimal('0.00'), 1L, '40', 'X10 Appliance Module', 'HOMEAUTO'), 'WPIR': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '50', 'Motion Detector', 'SENSOR'), 'TWODAY': ('SHIPPING', 'N/A', Decimal('29.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Two-Day Shipping', 'SHIPPING'), 'SL': ('PART', '19.95', Decimal('29.99'), 'N/A', Decimal('0.00'), 1L, '15', 'Solar Yard Sign Light', 'ACCESSORY'), 'WSRN': ('PART', '79.00', Decimal('99.99'), 'N/A', Decimal('0.00'), 1L, '50', 'X10 Siren', 'HOMEAUTO')},
                    #24:
                    'csp:2014-03-18': {'RKT': ('PART', '79.00', Decimal('99.99'), 'N/A', Decimal('0.00'), 1L, '45', 'X10 Socket Rocket', 'HOMEAUTO'), 'WSMOKE': ('PART', '125.00', Decimal('149.99'), 'N/A', Decimal('0.00'), 1L, '75', 'Smoke Detector', 'FIRE'), 'BUSINESS': ('PACKAGE', 'N/A', Decimal('99.00'), '99.00', Decimal('28.99'), 0L, 'N/A', 'Business', 'PACKAGE'), 'MINI': ('PART', '30.00', Decimal('30.00'), 'N/A', Decimal('0.00'), 1L, '25', 'Mini Pinpad', 'ACCESSORY'), 'ZLKTS': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '260', 'Z-Wave Touchscreen Lock -Satin Nickel', 'HOMEAUTO'), 'ZLKTO': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '260', 'Z-Wave Touchscreen Lock -Oil Rubbed Bronze', 'HOMEAUTO'), '2TP': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '65', 'Talking Wireless Keypad', 'ACCESSORY'), 'VIDEOSERVICE': ('PART', '0.00', Decimal('0.00'), 'N/A', Decimal('5.00'), 0L, '0', 'Additional Video Service', 'VIDEO'), 'PLATINUM': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('42.99'), 0L, 'N/A', 'Platinum', 'PACKAGE'), 'GOLD': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('39.99'), 0L, 'N/A', 'Gold', 'PACKAGE'), 'XT-2WTTS': ('PART', '115.00', Decimal('115.00'), 'N/A', Decimal('0.00'), 1L, '65', 'Simon XT Touch Screen Keypad', 'ACCESSORY'), 'SILVER': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('37.99'),0L, 'N/A', 'Silver', 'PACKAGE'), 'CAMERA': ('PART', '199.00', Decimal('249.99'), 'N/A', Decimal('0.00'), 0L, '125', 'Video Camera', 'VIDEO'), 'VIDEO': ('SERVICE', 'N/A', Decimal('0.00'), '0.00', Decimal('10.00'), 0L, 'N/A', 'Interactive Video Service', 'SERVICE'), 'ZLKTB':('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '260', 'Z-Wave Touchscreen Lock - Polished Brass', 'HOMEAUTO'), 'CELLCONV': ('MONITORING', 'N/A', Decimal('0.00'), '99.00', Decimal('0.00'), 0L, 'N/A', 'Cellular Conversion', 'MONITORING'), 'WPANIC': ('PART', '95.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '60', 'Medical Panic Pendant', 'ACCESSORY'), 'GPS': ('SERVICE', 'N/A', Decimal('0.00'), '99.00', Decimal('9.99'), 0L, 'N/A', 'GPS Tracking', 'SERVICE'), 'TWOWAY': ('MONITORING', 'N/A', Decimal('0.00'), '149.00', Decimal('5.00'), 0L, 'N/A', 'Two-Way Voice', 'MONITORING'), 'OVERNIGHT': ('SHIPPING', 'N/A', Decimal('49.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Overnight Shipping', 'SHIPPING'), 'WGLASS': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '50', 'Glass Break Detector', 'SENSOR'), 'COPPER': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('29.99'), 0L, 'N/A', 'Copper', 'PACKAGE'), 'UTA': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('10.00'), 0L, '50', 'GPS Tracking Device', 'GPS'), 'BROADBAND': ('MONITORING', 'N/A', Decimal('0.00'), '149.00', Decimal('8.00'), 0L, 'N/A', 'Broadband', 'MONITORING'), 'SIMONXT': ('PART', '299.00', Decimal('399.00'), 'N/A', Decimal('0.00'), 0L, '125', 'Simon XT Control Panel', 'PANEL'), 'FREEZE': ('PART', '125.00', Decimal('149.99'), 'N/A', Decimal('0.00'), 1L, '50', 'Freeze Sensor', 'SENSOR'), 'FLOOD': ('PART', '125.00', Decimal('149.99'), 'N/A', Decimal('0.00'), 1L, '60', 'Flood Sensor', 'SENSOR'), 'CELLULAR': ('MONITORING', 'N/A', Decimal('0.00'), '199.00', Decimal('12.00'), 0L, 'N/A', 'Cellular', 'MONITORING'), 'WCONT': ('PART', '39.50', Decimal('49.99'), 'N/A', Decimal('0.00'), 1L, '25', 'Micro Door/Window Sensor', 'SENSOR'), 'STANDARD': ('MONITORING', 'N/A', Decimal('0.00'), '99.00', Decimal('0.00'), 0L, 'N/A', 'Standard', 'MONITORING'), '4KEY': ('PART', '49.50', Decimal('69.99'), 'N/A', Decimal('0.00'), 1L, '25', '4-Button Keychain Remote Control', 'ACCESSORY'), 'BRONZE': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('35.99'), 0L, 'N/A', 'Bronze', 'PACKAGE'), 'GROUND': ('SHIPPING', 'N/A', Decimal('19.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Ground Shipping', 'SHIPPING'), 'SIMON3': ('PART', '299.00', Decimal('350.00'), 'N/A', Decimal('0.00'), 0L, '125', 'Simon 3', 'PANEL'), 'GARAGE': ('PART', '0.00', Decimal('0.00'), 'N/A', Decimal('2.00'), 1L, '40', 'Overhead Garage Door Sensor', 'SENSOR'), 'LAMP': ('PART', '79.00', Decimal('99.99'), 'N/A', Decimal('0.00'), 1L, '40', 'X10 Appliance Module', 'HOMEAUTO'), 'WPIR': ('PART', '99.00', Decimal('129.99'), 'N/A', Decimal('0.00'), 1L, '50', 'Motion Detector', 'SENSOR'), 'TWODAY': ('SHIPPING', 'N/A', Decimal('29.95'), 'N/A', Decimal('0.00'), 0L, 'N/A','Two-Day Shipping', 'SHIPPING'), 'SL': ('PART', '19.95', Decimal('29.99'), 'N/A', Decimal('0.00'), 1L, '15', 'Solar Yard Sign Light', 'ACCESSORY'), 'WSRN': ('PART', '79.00', Decimal('99.99'), 'N/A', Decimal('0.00'), 1L, '50', 'X10 Siren', 'HOMEAUTO'), 'DGSKT': ('PART', '15.00', Decimal('15.00'), 'N/A', Decimal('0.00'), 1L, '15', 'Yale Lock Thin Door Gasket', 'HOMEAUTO'), 'UPLINK': ('PART', '0.00', Decimal('0.00'), 'N/A', Decimal('0.00'), 0L, '0', 'Takeover Device', 'PANEL')},
                    #29:
                    'inside:2014-03-18': {'WSMOKE': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '45', 'Smoke Detector', 'FIRE'), 'SMOKE': ('SERVICE', 'N/A', Decimal('0.00'), '0.00', Decimal('2.00'), 0L, 'N/A', 'Smoke Detector Monitoring', 'SERVICE'), 'BUSINESS': ('PACKAGE', 'N/A', Decimal('99.00'), '99.00', Decimal('28.99'), 0L, 'N/A', 'Business', 'PACKAGE'), 'RE924': ('PART', '35.00', Decimal('35.00'), 'N/A', Decimal('0.00'), 1L, '15', 'Z-Wave Daughter Board', 'HOMEAUTO'), 'WCONTR': ('PART', '69.00', Decimal('69.00'), 'N/A', Decimal('0.00'), 1L, '25', 'RecessedDoor/Window Switch Sensor', 'SENSOR'), 'REP': ('PART', '199.00', Decimal('199.00'), 'N/A', Decimal('0.00'), 1L, '140', 'Wireless Repeater', 'SENSOR'), 'TWODAY': ('SHIPPING', 'N/A', Decimal('29.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Two-Day Shipping', 'SHIPPING'), 'WROT': ('PART', '89.00', Decimal('89.00'), 'N/A', Decimal('0.00'), 1L, '35', 'Wireless Router', 'ACCESSORY'), 'ZLAMPA': ('PART', '79.00', Decimal('79.00'), 'N/A', Decimal('0.00'), 1L, '30', 'Z-Wave Lamp & Appliance Module', 'HOMEAUTO'), 'YRDSIGN': ('PART', '12.00', Decimal('12.00'), 'N/A', Decimal('0.00'), 1L, '5', 'Yard Warning Sign', 'ACCESSORY'), '2TP': ('PART', '119.00', Decimal('119.00'), 'N/A', Decimal('0.00'), 1L, '50', 'Talking Wireless Keypad', 'ACCESSORY'), 'WCONTC': ('PART', '69.00', Decimal('69.00'), 'N/A', Decimal('0.00'), 1L, '30', 'Crystal Door/Window Sensor', 'SENSOR'), 'CARBON': ('SERVICE', 'N/A', Decimal('0.00'), '0.00', Decimal('2.00'), 0L, 'N/A', 'Carbon Monoxide Monitoring', 'SERVICE'), '2BPANIC': ('PART', '39.00', Decimal('39.00'), 'N/A', Decimal('0.00'), 1L, '10', '2-Button Panic Device', 'SENSOR'), 'WCARBON': ('PART', '129.00', Decimal('129.00'), 'N/A', Decimal('0.00'), 1L, '65', 'Carbon Monoxide Detector', 'FIRE'), 'MINI': ('PART', '49.00', Decimal('49.00'), 'N/A', Decimal('0.00'), 1L, '15', 'Mini Pinpad', 'ACCESSORY'), 'PLATINUM': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('42.99'), 0L, 'N/A', 'Platinum', 'PACKAGE'), 'GOLD': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('39.99'), 0L, 'N/A', 'Gold', 'PACKAGE'), 'WPANICB': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '40', 'Medical Panic Bracelet', 'ACCESSORY'), 'WPANIC': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '40', 'Medical Panic Pendant', 'ACCESSORY'), 'RE103': ('PART', '69.00', Decimal('69.00'), 'N/A', Decimal('0.00'), 1L, '15', 'Resolutions Medical Panic', 'SENSOR'), 'SILVER': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('37.99'), 0L, 'N/A', 'Silver', 'PACKAGE'), 'STANDARD': ('MONITORING', 'N/A', Decimal('0.00'), '99.00', Decimal('0.00'), 0L, 'N/A', 'Standard', 'MONITORING'), 'CAMERA': ('PART', '179.00', Decimal('179.00'), 'N/A', Decimal('0.00'), 0L, '135', 'Video Camera', 'VIDEO'), 'VIDEO': ('SERVICE', 'N/A', Decimal('0.00'), '0.00', Decimal('10.00'), 0L, 'N/A', 'Interactive Video Service', 'SERVICE'), 'VIDEOSERVICE': ('PART', '0.00', Decimal('0.00'), 'N/A', Decimal('5.00'), 0L, '0', 'Additional Video Service', 'VIDEO'), 'CELLCONV': ('MONITORING', 'N/A', Decimal('0.00'), '99.00', Decimal('0.00'), 0L, 'N/A', 'Cellular Conversion', 'MONITORING'), 'WCONTRP': ('PART', '69.00', Decimal('69.00'), 'N/A', Decimal('0.00'), 1L, '25', 'Recessed Door/Window Plunger Sensor', 'SENSOR'), 'GPS': ('SERVICE', 'N/A', Decimal('0.00'), '99.00', Decimal('9.99'), 0L, 'N/A', 'GPS Tracking', 'SERVICE'), 'ZLAMPD': ('PART', '79.00', Decimal('79.00'), 'N/A', Decimal('0.00'), 1L, '30', 'Z-Wave Incandescent Light Dimmer', 'HOMEAUTO'), 'OVERNIGHT': ('SHIPPING', 'N/A', Decimal('49.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Overnight Shipping', 'SHIPPING'), 'WGLASS': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '40', 'Glass Break Detector', 'SENSOR'), 'COPPER': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('29.99'), 0L, 'N/A', 'Copper', 'PACKAGE'), 'UTA': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('10.00'), 0L, '100', 'GPS Tracking Device', 'GPS'), 'DECALD': ('PART', '2.25', Decimal('2.25'), 'N/A', Decimal('0.00'), 1L, '5', 'Door Warning Sticker', 'ACCESSORY'), 'BROADBAND': ('MONITORING', 'N/A', Decimal('0.00'), '149.00', Decimal('8.00'), 0L, 'N/A', 'Broadband', 'MONITORING'), 'SIMONXT': ('PART', '119.00', Decimal('119.00'), 'N/A', Decimal('0.00'), 0L, '55', 'Simon XT Control Panel', 'PANEL'), 'FREEZE': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '40', 'Freeze Sensor', 'SENSOR'), 'FLOOD': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '40', 'Flood Sensor', 'SENSOR'), 'DECALW': ('PART', '2.25', Decimal('2.25'), 'N/A', Decimal('0.00'), 1L, '5', 'Window Warning Sticker', 'ACCESSORY'), 'CELLULAR': ('MONITORING', 'N/A', Decimal('0.00'), '199.00', Decimal('12.00'), 0L, 'N/A', 'Cellular', 'MONITORING'), 'WCONT': ('PART', '39.00', Decimal('39.00'), 'N/A', Decimal('0.00'), 1L, '10', 'Micro Door/Window Sensor', 'SENSOR'), 'ZLKTS': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '190', 'Z-Wave Touchscreen Lock - Satin Nickel', 'HOMEAUTO'), '4KEY': ('PART', '49.00', Decimal('49.00'), 'N/A', Decimal('0.00'), 1L, '10', '4-Button Keychain Remote Control', 'ACCESSORY'), 'BRONZE': ('PACKAGE', 'N/A', Decimal('0.00'), '0.00', Decimal('35.99'), 0L, 'N/A', 'Bronze', 'PACKAGE'), 'GROUND': ('SHIPPING', 'N/A', Decimal('19.95'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'GroundShipping', 'SHIPPING'), 'XT-2WTTS': ('PART', '115.00', Decimal('115.00'), 'N/A', Decimal('0.00'), 1L, '65', 'Simon XT Touch Screen Keypad', 'ACCESSORY'), 'TWOWAY': ('MONITORING', 'N/A', Decimal('0.00'), '149.00', Decimal('5.00'), 0L, 'N/A', 'Two-Way Voice', 'MONITORING'), 'GARAGE': ('PART', '59.00', Decimal('59.00'), 'N/A', Decimal('0.00'), 1L, '20', 'Overhead Garage Door Sensor', 'SENSOR'), 'ZLKTO': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '190', 'Z-Wave Touchscreen Lock - Oil Rubbed Bronze', 'HOMEAUTO'), 'WPIR': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '20', 'Motion Detector', 'SENSOR'), 'UHS': ('PART', '0.00', Decimal('0.00'), 'N/A', Decimal('0.00'), 0L, '0', 'Cellular Takeover Device (UHS)', 'PANEL'), 'CA:STANDARD': ('SHIPPING', 'N/A', Decimal('55.00'), 'N/A', Decimal('0.00'), 0L, 'N/A', 'Standard Shipping via Federal Express', 'SHIPPING'), 'SL': ('PART', '19.00', Decimal('19.00'), 'N/A', Decimal('0.00'), 1L, '5', 'Solar Yard Sign Light', 'ACCESSORY'), 'DGSKT': ('PART', '15.00', Decimal('15.00'), 'N/A', Decimal('0.00'), 1L, '15', 'Yale Lock Thin Door Gasket', 'HOMEAUTO'), 'SRNR': ('PART', '99.00', Decimal('99.00'), 'N/A', Decimal('0.00'), 1L, '45', 'Resolutions Wireless Siren', 'SENSOR'), 'ZLKTB': ('PART', '279.00', Decimal('279.00'), 'N/A', Decimal('0.00'), 0L, '190', 'Z-Wave Touchscreen Lock - Polished Brass', 'HOMEAUTO')}
                }

for pt in PRICETABLES.values():
    pt.update(VIDEOPLUS= ('SERVICE', '5.00', Decimal('5.00'), 'N/A', Decimal('0.00'), 1L, '0', 'Video Plus service (more than one camera)', 'HOMEAUTO'))


def CreateDBEntries():
    """this thing calls all the others"""

    # a timers
    global_timer = time()
    global_counter = 0

    # price things
    global_counter += CreatePriceGroups()
    global_counter += CreatePriceTables()
    global_counter += CreatePGMemberships()

    # business entity things
    global_counter += CreateOrganizations()
    global_counter += CreateCampaigns()

    # producty things
    global_counter += CreateProducts()
    pts = [PriceTable.objects.get(pk=pricetable_id) for pricetable_id in PRICETABLES]
    for pt in pts:
        global_counter += CreateProductContents(pt)

    # actual price lists
    global_counter += CreateProductPrices()

    global_timer = time() - global_timer
    return global_timer, global_counter


def CreatePriceGroups():
    """make all the price groups"""

    object_counter = PriceGroup.objects.count()

    PriceGroup(name='Fake PG').save()
    PriceGroup(name='PG Thirteen').save() # lel

    return PriceGroup.objects.count() - object_counter


def CreatePriceTables():
    """make all the price tables"""

    object_counter = PriceTable.objects.count()

    for pt in PRICETABLES:
        PriceTable(pricetable_id=pt).save()

    return PriceTable.objects.count() - object_counter


def CreatePGMemberships():
    """attach the price tables to price groups with this through table"""

    object_counter = PGMembership.objects.count()

    # obtain some of the pts
    saveology = PriceTable.objects.get(pricetable_id='saveology:2014-03-18')
    csp = PriceTable.objects.get(pricetable_id='csp:2014-03-18')
    inside = PriceTable.objects.get(pricetable_id='inside:2014-03-18')

    # obtain the pgs
    fakepg = PriceGroup.objects.get(name='Fake PG')
    pgthirteen = PriceGroup.objects.get(name='PG Thirteen')

    PGMembership(pricegroup=fakepg, pricetable=saveology, notes='this is 2saveology', zorder=1, date_updated=datetime.now()).save()
    PGMembership(pricegroup=fakepg, pricetable=csp, notes='this is csp and should be overlaid with 26', zorder=0, date_updated=datetime.now()).save()
    PGMembership(pricegroup=pgthirteen, pricetable=inside, notes='this is inside', zorder=0, date_updated=datetime.now()).save()

    return PGMembership.objects.count() - object_counter


def CreateCampaigns():
    """make all the campaigns"""

    object_counter = Campaign.objects.count()

    # obtain an organization
    test = Organization.objects.get(org_code='testorg')

    # obtain a price group
    #fakepg = PriceGroup.objects.get(name='Fake PG')

    Campaign(campaign_id='X00000', name='Test Campaign', pricegroup=None, organization=test).save()

    return Campaign.objects.count() - object_counter


def CreateOrganizations():
    """make all the organizations"""

    object_counter = Organization.objects.count()

    # obtain a price group
    pgthirteen = PriceGroup.objects.get(name='PG Thirteen')

    Organization(org_code='testorg', name='Test Organization', pricegroup=pgthirteen).save()

    return Organization.objects.count() - object_counter


def CreateProducts():
    """make all the products by their child models"""

    # cheat with the inheritance
    object_counter = Product.objects.count()

    # deal with duplicates
    seen_list = set()

    for price_table in PRICETABLES.values():
        for product_code, data in price_table.iteritems():
            if product_code not in seen_list:
                context = dict(code=product_code, product_type=data[0].capitalize(), category=data[8].capitalize(), name=data[7], description='')

                if data[0] == 'PART':
                    Part(**context).save()
                elif data[0] == 'SERVICE':
                    context['category'] = 'Services'
                    Service(**context).save()
                elif data[0] == 'MONITORING':
                    context['category'] = 'Connection Method'
                    Monitoring(**context).save()
                elif data[0] == 'SHIPPING':
                    context['category'] = 'Shipping Method'
                    Shipping(**context).save()
                elif data[0] == 'PACKAGE':
                    context['category'] = 'Packages'
                    context['description'] = context['name'].capitalize() + ' Package'
                    Package(**context).save()
                else:
                    print data[0]

                seen_list.add(product_code)

    Product(code='PERMIT', product_type='Product', category='Fees and Licensing', name='Local Permit Fee', description='Permit fee collected for local jurisdiction').save()
    Closer(code='10RTDROP', product_type='Closer', category='Rate Drops', name='$10/mo rate drop', description='Removes $10 per month (requires manager approval)').save()
    Closer(code='5RTDROP', product_type='Closer', category='Rate Drops', name='$5/mo rate drop', description='Removes $5 from the monthly monitoring').save()
    Closer(code='FREEKEY', product_type='Closer', category='Rate Drops', name='Free Keychains', description='Give away some of our famous disposable keychains!').save()
    Closer(code='FREESHIP', product_type='Closer', category='Rate Drops', name='Free Shipping', description='Cancels out shipping cost for the customer').save()

    Combo(code='COMBOTEST', product_type='Combo', category='Combos', name='Test Combo', description='so combo wow much products').save()

    return Product.objects.count() - object_counter


def CreateProductContents(pt):
    """add contents to those products that require it"""

    object_counter = ProductContent.objects.count()

    # stuff we put in all packages
    wcont = Part.objects.get(code='WCONT')
    simonxt = Part.objects.get(code='SIMONXT')
    wpir = Part.objects.get(code='WPIR')

    # how many wcont are in each package
    wcont_qtys =  {
                'COPPER': 3,
                'BRONZE': 7,
                'SILVER': 10,
                'GOLD': 12,
                'PLATINUM': 15,
                'BUSINESS': 2,
            }

    # put these things in the packages with fake upfront strike prices
    for k, v in wcont_qtys.iteritems():
        current_package = Package.objects.get(code=k)
        ProductContent(pricetable=pt, included_in=current_package, included_product=wcont, quantity=v, upfront_strike=5.0, monthly_strike=None).save()
        ProductContent(pricetable=pt, included_in=current_package, included_product=simonxt, quantity=1, upfront_strike=5.0, monthly_strike=None).save()
        ProductContent(pricetable=pt, included_in=current_package, included_product=wpir, quantity=1, upfront_strike=5.0, monthly_strike=None).save()

    # stuff that goes in combos
    yrdsign = Part.objects.get(code='YRDSIGN')

    # combos
    testcombo = Combo.objects.get(code='COMBOTEST')

    # put stuff in the combos with fake upfront strike prices
    ProductContent(pricetable=pt, included_in=testcombo, included_product=yrdsign, quantity=2, upfront_strike=5.5, monthly_strike=None).save()

    return ProductContent.objects.count() - object_counter


def CreateProductPrices():
    """give prices to products on price tables without which they would not exist"""

    object_counter = ProductPrice.objects.count()

    # obtain pricetable models
    pts = { pt.pricetable_id: pt for pt in PriceTable.objects.all() }

    # iterate over PRICETABLES and write in the prices
    for name, pt in PRICETABLES.iteritems():
        for product, data in pt.iteritems():
            tempdata6 = None
            try:
                tempdata6 = int(data[6])
            except ValueError:
                pass

            context = dict(pricetable=pts[name], product=Product.objects.get(code=product), max_quantity=None, monthly_price=data[4] or None, upfront_price=data[2] or None, cb_points=tempdata6, fromdate=None, todate=None, promo=False, swappable=bool(data[5] or False))

            if data[0] == 'PART':
                context['max_quantity'] = 99
            elif data[0] == 'SERVICE':
                context['max_quantity'] = 1
            elif data[0] == 'MONITORING':
                context['max_quantity'] = 1
            elif data[0] == 'SHIPPING':
                context['max_quantity'] = 1
            elif data[0] == 'PACKAGE':
                context['max_quantity'] = 1
            else:
                print data[0]

            ProductPrice(**context).save()

        for combo in Combo.objects.all():
                ProductPrice(pricetable=pts[name], product=combo, max_quantity=99, monthly_price=None, upfront_price=7.0, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

        for closer in Closer.objects.filter(code__in=['FREEKEY', 'FREESHIP']):
            ProductPrice(pricetable=pts[name], product=closer, max_quantity=1, monthly_price=None, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

        ProductPrice(pricetable=pts[name], product=Closer.objects.get(code='10RTDROP'), max_quantity=1, monthly_price=-10.0, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()
        ProductPrice(pricetable=pts[name], product=Closer.objects.get(code='5RTDROP'), max_quantity=1, monthly_price=-5.0, upfront_price=None, cb_points=None, fromdate=None, todate=None, promo=False, swappable=False).save()

    return ProductPrice.objects.count() - object_counter

class Command(BaseCommand):
    help = 'adds trashboard\'s data fixtures to the database'

    def handle(self, *args, **kwargs):
        # advertise, create, and return
        self.stdout.write('[\033[94m{}\033[0m] adding fixtures...'.format(NAME))
        timer, counter = CreateDBEntries()
        self.stdout.write('[\033[94m{}\033[0m] \033[01m{}\033[0m model(s) created in \033[01m{}\033[0m second(s)'.format(NAME, counter, timer))
