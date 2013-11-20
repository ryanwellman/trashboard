# import built-ins
import json
from json import dumps, loads
from random import choice

# import 3rd-party modules
from annoying.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from dynamicresponse.response import *

# import from self (models)
from agreement.models import Agreement

@csrf_exempt
def dyn_json(request, agreement_id=None):
    # attempts to get or set a specific agreement
    # this is csrf_exempt so i can test it with curl
    agreement = None
    blob = {}

    if agreement_id:
        # user wants a specific agreement
        agreement = get_object_or_404(Agreement.objects.all(), pk=agreement_id)
        blob = agreement.serialize()

    if request.method == 'POST':
        for key in request.POST:    # request.POST is fucked up when sending JSON
            incoming = loads(key)

        # does blob exist?
        if blob:
            # we are updating an existing one
            agreement.update_from_dict(incoming)
        else:
            # we are creating a new one so obtain json from post
            blob = incoming

            # create and save it
            agreement = Agreement.objects.create(**blob)
            agreement.save()

    return SerializeOrRedirect(reverse(draw_test), blob)


def serve_json(request):
    # returns a random agreement as json
    agreement = Agreement.objects.order_by('?')[0]
    # this next one will be better as soon as there are any objects in the database
    # agreement = Agreement.objects.raw('SELECT * FROM agreement_agreement ORDER BY RAND() LIMIT 1')

    ctx = agreement.serialize()
    return SerializeOrRedirect(reverse(draw_test), ctx)


def test_json(request):
    # sends json response given in the dictionary below
    ctx =   {
                'fname':    'al',
                'lname':    'smif',
                'initial':  'h',
                'address':  '92103 chainsaw place',
                'city':     'marfa',
                'state':    'tx'.upper(),
                'zip':      '12345',
                'country':  'usa'.upper(),
                'taxid':    '123-45-6780',
                'email':    'al@smif.com',
                'approved': 'approved',
                'package':  'copper',
                'shipping': 'jpost',
                'arrtest':  ['jeff', 'jones', 'legit'],
            }

    return SerializeOrRedirect(reverse(draw_test), ctx)


@render_to('templates/container.html')
def draw_container(request):
    # uses render_to to draw the template

    # this is a dummy view that will render a dummy form that is simply to demo
    # the possibilities that come with the new agreement form

    # in reality these values would be coming from the models in pricemodels.py
    # right now there is no actual Agreement model other than the dummy one in the
    # agreement app

    # for the following 4 lists of dictionaries:
    # from Product: name <-> name, description <-> description
    # from ProductPrice price <-> price
    premiums    =  [    {'name':'Camera Add-on', 'price':'$49.99', 'description': 'Watch your home from somewhere else!'},
                        {'name':'Cellular Service', 'price':'$79.99', 'description': 'Cut the wires and it still works!'},
                        {'name':'GPS', 'price':'$99.99', 'description': 'Let first responders know where you are at all times!'}    ]

    combos      =  [    {'name':'3 Keypads', 'price':'$99.99', 'description': 'Great for households with children!'},
                        {'name':'Many Keychains', 'price':'$29.99', 'description': 'So cheap they\'re disposable!'},
                        {'name':'Solar Alarm Add-on Kit', 'price':'$159.99', 'description': 'For the consumer with no grid power!'}    ]

    services    =  [    {'name':'Video Service', 'price':'$19.99/mo', 'reason': 'cameras'},
                        {'name':'Smoke Service', 'price':'$29.99/mo', 'reason': 'smoke detector(s)'},
                        {'name':'Alpaca Rental Service', 'price':'$159.99/mo', 'reason': 'alpaca shears'}    ]

    closers     =  [    {'name': '$5/mo rate drop', 'description': 'Removes $5 from the monthly monitoring rate'},
                        {'name': '$10/mo rate drop', 'description': 'Removes $10 (requires manager approval)'},
                        {'name': 'Free Keychains', 'description': 'Give away some of our famous disposable keychains'},
                        {'name': 'Free Shipping', 'description': 'Cancels out shipping cost for the customer'}  ]

    # this one is going to come from the Package class and will change later
    packages    =  [    {'name':'Copper', 'price':'$19.99/mo', 'xt':'1', 'dw':'3', 'mot':'1'},
                        {'name':'Bronze', 'price':'$35.99/mo', 'xt':'1', 'dw':'7', 'mot':'1'},
                        {'name':'Silver', 'price':'$37.99/mo', 'xt':'1', 'dw':'10', 'mot':'1'},
                        {'name':'Gold', 'price':'$39.99/mo', 'xt':'1', 'dw':'12', 'mot':'1'},
                        {'name':'Platinum', 'price':'$42.99/mo', 'xt':'1', 'dw':'15', 'mot':'1'}    ]

    return dict(premiums=premiums, combos=combos, services=services, closers=closers, packages=packages)


@render_to('templates/package.html')
def Package(request):
    ko_packages = [{'code':'copper', 'name':'Copper', 'contents':[{'code':'DWSENS', 'quantity':'3' },
                                                                  {'code':'SIMNXT', 'quantity':'1' },
                                                                  {'code':'MOTDEC', 'quantity':'2' }
                                                              ]},
                {'code':'bronze', 'name':'Bronze', 'contents':[{'code':'DWSENS', 'quantity':'7' },
                                                               {'code':'SIMNXT', 'quantity':'1' },
                                                               {'code':'MOTDEC', 'quantity':'2' }
                                                              ]},
                {'code':'silver', 'name':'Silver', 'contents':[{'code':'DWSENS', 'quantity':'10' },
                                                               {'code':'SIMNXT', 'quantity':'1' },
                                                               {'code':'MOTDEC', 'quantity':'2'  }
                                                              ]},
                {'code':'gold', 'name':'Gold', 'contents':[{'code':'DWSENS', 'quantity':'12' },
                                                           {'code':'SIMNXT', 'quantity':'1' },
                                                           {'code':'MOTDEC', 'quantity':'2' }
                                                           ]},
                {'code':'platinum', 'name':'Platinum', 'contents':[{'code':'DWSENS', 'quantity':'15' },
                                                                   {'code':'SIMNXT', 'quantity':'1' },
                                                                   {'code':'MOTDEC', 'quantity':'2' }
                                                                  ]}]

    ko_parts = [{'code':'DWSENS', 'name':'Door/Window Sensors', 'points':'5', 'quantity':'0', 'category':'Security Sensors', 'price':'39.50'},
                {'code':'GBSENS', 'name':'Glass Break Sensor', 'points':'10', 'quantity':'0', 'category':'Security Sensors', 'price':'99.00'},
                {'code':'LTSENS', 'name':'Low Temperature Sensor', 'points':'10', 'quantity':'0', 'category':'Security Sensors', 'price':'125.00'},
                {'code':'MOTDEC', 'name':'Motion Detector', 'points':'10', 'quantity':'0', 'category':'Security Sensors', 'price':'99.00'},
                {'code':'FLSENS', 'name':'Flood Sensor', 'points':'12', 'quantity':'0', 'category':'Security Sensors', 'price':'125.00'},
                {'code':'GDSENS', 'name':'Garage Door Sensor', 'points':'8', 'quantity':'0', 'category':'Security Sensors', 'price':'39.50'},
                {'code':'KEYCRC', 'name':'Keychain Remote Control', 'points':'5', 'quantity':'0', 'category':'Accessories', 'price':'49.50'},
                {'code':'MEDPNB', 'name':'Medical Panic Bracelet', 'points':'10', 'quantity':'0', 'category':'Accessories', 'price':'95.00'},
                {'code':'MEDPEN', 'name':'Medical Panic Pendant', 'points':'12', 'quantity':'0', 'category':'Accessories', 'price':'95.00'},
                {'code':'MINPNP', 'name':'Mini Pinpad', 'points':'5', 'quantity':'0', 'category':'Accessories', 'price':'30.00'},
                {'code':'SOLLGT', 'name':'Solar Light', 'points':'3', 'quantity':'0', 'category':'Accessories', 'price':'19.95'},
                {'code':'TLKKYP', 'name':'Talking Keypad', 'points':'13', 'quantity':'0', 'category':'Accessories', 'price':'99.00'},
                {'code':'TLKTSC', 'name':'XT Talking Touchscreen', 'points':'13', 'quantity':'0', 'category':'Accessories', 'price':'115.00'},
                {'code':'SMKDET', 'name':'Smoke Detector', 'points':'15', 'quantity':'0', 'category':'Fire Sensors', 'price':'99.00'},
                {'code':'CRBMDT', 'name':'Carbon Monoxide Detector', 'points':'10', 'quantity':'0', 'category':'Fire Sensors', 'price':'99.00'},
                {'code':'XTNSIR', 'name':'XT Siren', 'points':'10', 'quantity':'0', 'category':'Home Automation', 'price':'79.00'},
                {'code':'XTSRCK', 'name':'X10 Socket Rocket', 'points':'9', 'quantity':'0', 'category':'Home Automation', 'price':'79.00'},
                {'code':'XTNAPM', 'name':'X10 Appliance Module', 'points':'9', 'quantity':'0', 'category':'Home Automation', 'price':'79.00'},
                {'code':'SIMTHR', 'name':'Simon 3', 'points':'25', 'quantity':'0', 'category':'Security Panels', 'price':'299.00'},
                {'code':'SIMNXT', 'name':'Simon XT', 'points':'25', 'quantity':'0', 'category':'Security Panels', 'price':'299.00'},
                {'code':'TLKDEV', 'name':'Talkover Device', 'points':'10', 'quantity':'0', 'category':'Security Panels', 'price':'199.00'}]

    ko_categories = {'Security Sensors':['DWSENS', 'GBSENS', 'LTSENS', 'MOTDEC', 'FLSENS', 'GDSENS'],
                     'Accessories':['KEYCRC', 'MEDPNB', 'MEDPEN', 'MINPNP', 'SOLLGT', 'TLKKYP', 'TLKTSC'],
                     'Fire Sensors':['SMKDET', 'CRBMDT'],
                     'Home Automation':['XTNSIR', 'XTSRCK', 'XTNAPM'],
                     'Security Panels':['SIMTHR', 'SIMNXT', 'TLKDEV']}

    json_ko_packages = dumps(ko_packages)
    json_ko_parts = dumps(ko_parts)
    json_ko_categories = dumps(ko_categories)

    return dict(json_ko_packages=json_ko_packages,
                json_ko_parts=json_ko_parts,
                json_ko_categories=json_ko_categories)


@render_to('templates/dyntest.html')
def draw_test(request):
    return dict()


@render_to('templates/purchase.html')
def Purchase(request):
    ko_parts = [{'code':'DWSENS', 'name':'Door/Window Sensors', 'points':'5', 'quantity':'0', 'category':'Security Sensors', 'price':'39.50'},
                {'code':'GBSENS', 'name':'Glass Break Sensor', 'points':'10', 'quantity':'0', 'category':'Security Sensors', 'price':'99.00'},
                {'code':'LTSENS', 'name':'Low Temperature Sensor', 'points':'10', 'quantity':'0', 'category':'Security Sensors', 'price':'125.00'},
                {'code':'MOTDEC', 'name':'Motion Detector', 'points':'10', 'quantity':'0', 'category':'Security Sensors', 'price':'99.00'},
                {'code':'FLSENS', 'name':'Flood Sensor', 'points':'12', 'quantity':'0', 'category':'Security Sensors', 'price':'125.00'},
                {'code':'GDSENS', 'name':'Garage Door Sensor', 'points':'8', 'quantity':'0', 'category':'Security Sensors', 'price':'39.50'},
                {'code':'KEYCRC', 'name':'Keychain Remote Control', 'points':'5', 'quantity':'0', 'category':'Accessories', 'price':'49.50'},
                {'code':'MEDPNB', 'name':'Medical Panic Bracelet', 'points':'10', 'quantity':'0', 'category':'Accessories', 'price':'95.00'},
                {'code':'MEDPEN', 'name':'Medical Panic Pendant', 'points':'12', 'quantity':'0', 'category':'Accessories', 'price':'95.00'},
                {'code':'MINPNP', 'name':'Mini Pinpad', 'points':'5', 'quantity':'0', 'category':'Accessories', 'price':'30.00'},
                {'code':'SOLLGT', 'name':'Solar Light', 'points':'3', 'quantity':'0', 'category':'Accessories', 'price':'19.95'},
                {'code':'TLKKYP', 'name':'Talking Keypad', 'points':'13', 'quantity':'0', 'category':'Accessories', 'price':'99.00'},
                {'code':'TLKTSC', 'name':'XT Talking Touchscreen', 'points':'13', 'quantity':'0', 'category':'Accessories', 'price':'115.00'},
                {'code':'SMKDET', 'name':'Smoke Detector', 'points':'15', 'quantity':'0', 'category':'Fire Sensors', 'price':'99.00'},
                {'code':'CRBMDT', 'name':'Carbon Monoxide Detector', 'points':'10', 'quantity':'0', 'category':'Fire Sensors', 'price':'99.00'},
                {'code':'XTNSIR', 'name':'XT Siren', 'points':'10', 'quantity':'0', 'category':'Home Automation', 'price':'79.00'},
                {'code':'XTSRCK', 'name':'X10 Socket Rocket', 'points':'9', 'quantity':'0', 'category':'Home Automation', 'price':'79.00'},
                {'code':'XTNAPM', 'name':'X10 Appliance Module', 'points':'9', 'quantity':'0', 'category':'Home Automation', 'price':'79.00'},
                {'code':'SIMTHR', 'name':'Simon 3', 'points':'25', 'quantity':'0', 'category':'Security Panels', 'price':'299.00'},
                {'code':'SIMNXT', 'name':'Simon XT', 'points':'25', 'quantity':'0', 'category':'Security Panels', 'price':'299.00'},
                {'code':'TLKDEV', 'name':'Talkover Device', 'points':'10', 'quantity':'0', 'category':'Security Panels', 'price':'199.00'}]

    json_ko_parts = dumps(ko_parts)

    return dict(json_ko_parts=json_ko_parts)
