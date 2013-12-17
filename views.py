# import built-ins
from json import dumps, loads
from itertools import chain

# import 3rd-party modules
from annoying.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from dynamicresponse.response import SerializeOrRedirect

# import from self (models)
from agreement.models import *
from pricefunctions import *

@csrf_exempt
def dyn_json(request, agreement_id=None):
    """
    reads or updates an Agreement and returns it to the caller as json

    XXX: eventually this will need to accept a campaign id as well
    """

    # attempts to get or set a specific agreement
    agreement = None
    response = None
    campaign = Campaign.objects.all()[0]
    blankp = Package.objects.filter(code='blank')[0]

    # handle obtaining an agreement object
    if agreement_id:
        # user wants a specific agreement
        agreement = get_object_or_404(Agreement.objects.all(), pk=agreement_id)
    else:
        # make a new agreement with non-optional blank child models included
        agreement = Agreement(campaign=campaign, package=blankp, applicant=Applicant(), billing_address=Address(), system_address=Address())

    # handle outgoing data
    if request.method == 'GET':
        response = agreement.serialize(ignore=['campaign', 'pricetable_date'])
        # DEBUG: add things that make this form actually work but don't save completely yet
        ctx =   {
                    'premium': {
                        'selected_codes': [],
                        'contents': [],
                        'done': agreement.done_premium,
                    },
                    'combo': {
                        'selected_codes': [],
                        'contents': [],
                        'done': agreement.done_combo,
                    },
                    'customize': {
                        'purchase_lines': [],
                        'done': agreement.done_customize,
                    },
                    'closing': {
                        'done': agreement.done_closing,
                    },
                    'services_and_promos': {
                        'done': agreement.done_promos,
                    },
                }
        response.update(ctx);

        # DEBUG: fix package
        code = ''
        if not agreement.package.code == 'blank':
            code = agreement.package.code
        ctx =   {
                    'selected_package': {
                        'code': agreement.package.code,
                    },
                    'customizing': False,
                    'cb_balance': '0',
                    'updated_contents': [],
                    'changed_contents': False,
                    'customization_lines': [],
                    'done': agreement.done_package,
                }
        response['package'] = ctx
        response.pop('done_package', None)
        response.pop('done_premium', None)
        response.pop('done_combo', None)
        response.pop('done_customize', None)
        response.pop('done_closing', None)
        response.pop('done_promos', None)

        # obtain the invoice lines for this agreement
        ilines = InvoiceLine.objects.filter(agreement=agreement)
        
        # turn invoice lines into quantities
        for iline in ilines:
            pass

    # handle incoming data
    if request.method == 'POST':
        for key in request.POST:    # request.POST is fucked up when sending JSON
            incoming = loads(key)
            print incoming

        # DEBUG: save agreement state
        agreement.done_premium = incoming.get('premium').get('done')
        agreement.done_combo = incoming.get('combo').get('done')
        agreement.done_customize = incoming.get('customize').get('done')
        agreement.done_closing = incoming.get('closing').get('done')
        agreement.done_package = incoming.get('package').get('done')
        agreement.done_promos = incoming.get('services_and_promos').get('done')

        # save some of the things we're splitting off
        premiums = incoming.pop('premium',None)
        combos = incoming.pop('combo',None)
        customs = incoming.pop('customize',None)
        incoming.pop('closing',None)
        incoming.pop('services_and_promos', None)

        # DEBUG: fix package field
        selpkg = incoming.get('package').get('selected_package')
        if selpkg:
            selpkg_code = selpkg.get('code') or ''
        else:
            selpkg_code = ''

        packages = Package.objects.filter(code=selpkg_code)
        if packages:
            agreement.package = packages[0]

        incoming.pop('package', None)

        # handle invoice lines by first deleting them all and obtaining a price list
        InvoiceLine.objects.filter(agreement=agreement).delete()
        pricelist = get_productprice_list(campaign)
        for pp in pricelist:
            fantastic_pricelist[pp.product.code] = dict(monthly_each=int(pp.monthly_price or 0), upfront_each=int(pp.upfront_price or 0))

        # now loop through the things that need invoice lines
        for selected in chain(premiums.get('selected_codes'), combos.get('selected_codes')):
            # obtain the orm product associated with this code
            selected_product = Product.objects.filter(code=selected.code)[0]

            # assemble the pieces into a context
            ilinectx = dict(agreement=agreement, note='', product=selected.code, quantity=selected.quantity, pricedate=timezone.now)
            ilinectx.update(fantastic_pricelist[selected.code])
            ilinectx['monthly_total'] = selected.quantity * int(ilinectx.get('monthly_each') or 0)
            ilinectx['upfront_total'] = selected.quantity * int(ilinectx.get('upfront_each') or 0)

            # actually create this invoice line
            iline = InvoiceLine(**ilinectx)
            iline.save()

            # now handle children of this last line
            for children in selected.contents:
                # obtain this thing's combo line to get its strikeout prices
                child_product = Product.objects.filter(code=children.code)[0]
                cline = ComboLine.objects.filter(parent=selected_product, product=child_product)[0]

                # assemble these pieces
                ichildctx = dict(agreement=agreement, note='', product=children.code, quantity=children.quantity, pricedate=timezone.now, parent=iline)
                ichildctx['monthly_strike'] = cline.monthly_strike
                ichildctx['upfront_strike'] = cline.upfront_strike

                # actually create it
                ichild = InvoiceLine(**ichildctx)
                ichild.save()

        # update agreement with values from incoming
        agreement.update_from_dict(incoming)

        # create a response
        response = agreement.serialize(ignore=['campaign'])

    if request.method == 'PUT':
        pass

    if request.method == 'DELETE':
        pass

    return SerializeOrRedirect(reverse(draw_test), response)


def serve_json(request):
    """
    gets and returns a random agreement as json (debug)
    """
    # returns a random agreement as json
    agreement = Agreement.objects.order_by('?')[0]
    # this next one will be better as soon as there are any objects in the database
    # agreement = Agreement.objects.raw('SELECT * FROM agreement_agreement ORDER BY RAND() LIMIT 1')

    ctx = agreement.serialize()
    return SerializeOrRedirect(reverse(draw_test), response)


def test_json(request):
    """
    returns a contrived agreement as json (debug)
    """
    # sends json response given in the dictionary below
    ctx =   {
                'applicant': {
                    'fname':    '',
                    'lname':    '',
                    'initial':  '',
                },
                'billing_address': {
                    'address':  '',
                    'city':     '',
                    'state':    '',
                    'zip':      '',
                    'country':  '',
                },
                'email':    '',
                'approved': '',
                'package':  {
                    'selected_package': {
                        'code': '',
                        'name': '',
                    },
                    'customizing': False,
                    'cb_balance': '0',
                    'updated_contents': [],
                    'changed_contents': False,
                    'customization_lines': [],
                    'done': False,
                },
                'shipping': '',
                'monitoring': '',
                'floorplan': '',
                'promo_code':'',
                'premium': {
                    'selected_codes': [],
                    'contents': [],
                    'done': False,
                },
                'combo': {
                    'selected_codes': [],
                    'contents': [],
                    'done': False,
                },
                'customize': {
                    'purchase_lines': [],
                    'done': False,
                },
                'closing': {
                    'done': False,
                },
                'services_and_promos': {
                    'done': False,
                },
            }

    return SerializeOrRedirect(reverse(draw_test), ctx)


@render_to('container.html')
def draw_container(request, agreement_id=None):
    """
    renders an agreement form container to the caller along with its parts
    """
    # fix agreement_id
    if agreement_id is None:
        agreement_id = ''

    # 404 non-existent ones
    if agreement_id:
        agreement = get_object_or_404(Agreement.objects.all(), pk=agreement_id)

    # this is a dummy view that will render a dummy form that is simply to demo
    # the possibilities that come with the new agreement form

    # in reality these values would be coming from the models in pricemodels.py
    # as collections of ProductPrice objects (?)

    # right now there is no actual Agreement model other than the dummy one in the
    # agreement app

    # XXX: eventually people should be getting these lists of things from somewhere else by campaign

    # for the following 4 lists of dictionaries:
    # from Product: code <-> code, name <-> name, description <-> description
    # this next one will actually be two prices per pricemodels.py
    # from ProductPrice price <-> price


    premiums    =  [    {'code':'CAMERA', 'name':'Camera Add-on', 'price':'$49.99', 'description': 'Watch your home from somewhere else!', 'contents': [{'code':'CAMERA', 'quantity':'1',},],},
                        {'code':'CELLANT', 'name':'Cellular Antenna', 'price':'$79.99', 'description': 'Cut the wires and it still works!', 'contents': [{'code':'CELLANT', 'quantity':'1'},{'code':'CELLSERV', 'quantity':'1',},],},
                        {'code':'GPS', 'name':'GPS', 'price':'$99.99', 'description': 'Let first responders know where you are at all times!', 'contents': [{'code':'GPS', 'quantity':'1',},{'code':'GPSSERV', 'quantity':'1'}],}    ]

    combos      =  [    {'code':'3KEYS', 'name':'3 Keypads', 'price':'$99.99', 'description': 'Great for households with children!', 'contents': [{'code':'KEYPAD', 'quantity':'3',},], },
                        {'code':'MANYKEY', 'name':'Many Keychains', 'price':'$29.99', 'description': 'So cheap they\'re disposable!', 'contents': [{'code':'KEYCHAIN', 'quantity':'10',},], },
                        {'code':'SOLAR', 'name':'Solar Alarm Add-on Kit', 'price':'$159.99', 'description': 'For the consumer with no grid power!', 'contents': [{'code':'ALRMBATT', 'quantity': '1'},{'code':'SOLARPANEL', 'quantity':'1',},], },    ]

    services    =  [    {'code':'VIDEOSRV', 'name':'Video Service', 'price':'$19.99/mo', 'reason': 'cameras'},
                        {'code':'SMOKESRV', 'name':'Smoke Service', 'price':'$29.99/mo', 'reason': 'smoke detector(s)'},
                        {'code':'ALPACASRV', 'name':'Alpaca Rental Service', 'price':'$159.99/mo', 'reason': 'alpaca shears'}    ]

    closers     =  [    {'code':'5RTDROP', 'name': '$5/mo rate drop', 'description': 'Removes $5 from the monthly monitoring rate'},
                        {'code':'10RTDROP', 'name': '$10/mo rate drop', 'description': 'Removes $10 (requires manager approval)'},
                        {'code':'FREEKEY', 'name': 'Free Keychains', 'description': 'Give away some of our famous disposable keychains'},
                        {'code':'FREESHIP', 'name': 'Free Shipping', 'description': 'Cancels out shipping cost for the customer'}  ]

    # this one is going to come from the Package class and will change later
    packages    =  [    {'code':'copper', 'name':'Copper', 'contents':[{'code':'DWSENS', 'quantity':'3' },{'code':'SIMNXT', 'quantity':'1' },{'code':'MOTDEC', 'quantity':'2' }]},
                        {'code':'bronze', 'name':'Bronze', 'contents':[{'code':'DWSENS', 'quantity':'7' },{'code':'SIMNXT', 'quantity':'1' },{'code':'MOTDEC', 'quantity':'2' }]},
                        {'code':'silver', 'name':'Silver', 'contents':[{'code':'DWSENS', 'quantity':'10' },{'code':'SIMNXT', 'quantity':'1' },{'code':'MOTDEC', 'quantity':'2'  }]},
                        {'code':'gold', 'name':'Gold', 'contents':[{'code':'DWSENS', 'quantity':'12' },{'code':'SIMNXT', 'quantity':'1' },{'code':'MOTDEC', 'quantity':'2' }]},
                        {'code':'platinum', 'name':'Platinum', 'contents':[{'code':'DWSENS', 'quantity':'15' },{'code':'SIMNXT', 'quantity':'1' },{'code':'MOTDEC', 'quantity':'2' }]}  ]

    parts       =  [    {'code':'DWSENS', 'name':'Door/Window Sensors', 'points':'5', 'quantity':'0', 'category':'Security Sensors', 'price':'39.50'},
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
                        {'code':'TLKDEV', 'name':'Talkover Device', 'points':'10', 'quantity':'0', 'category':'Security Panels', 'price':'199.00'}  ]

    return dict(gen_arrays(Campaign.objects.all()[0]), agreement_id=dumps(dict(agreement_id=agreement_id)))
    # uses render_to to draw the template
    #return dict(premiums=dumps(premiums), combos=dumps(combos), services=services, closers=closers, packages=dumps(packages), parts=dumps(parts), agreement_id=dumps(dict(agreement_id=agreement_id)))


@render_to('package.html')
def Packages(request):
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


@render_to('dyntest.html')
def draw_test(request):
    return dict()


@render_to('purchase.html')
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


@render_to('initial_info.html')
def InitialInfo(request):
    return dict()
