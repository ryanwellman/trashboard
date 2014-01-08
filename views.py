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
        # create a context of sorts
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
                    'alacarte': {
                        'purchase_lines': [],
                        'done': agreement.done_alacarte,
                    },
                    'closing': {
                        'selected_codes': [],
                        'done': agreement.done_closing,
                    },
                    'services_and_promos': {
                        'selected_codes': [],
                        'done': agreement.done_promos,
                    },
                }

        # package is its own can of worms
        code = ''
        if not agreement.package.code == 'blank':
            code = agreement.package.code
        packctx =   {
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

        # obtain the invoice lines for this agreement
        ilines = InvoiceLine.objects.filter(agreement=agreement)

        # obtain a price list and its associate fantastic version
        # this fantastic pricelist contains cb points instead of price table names
        pricelist = get_productprice_list(campaign)
        fantastic_pricelist = {}
        for pp in pricelist:
            fantastic_pricelist[pp.product.code] = dict(monthly_each=int(pp.monthly_price or 0), upfront_each=int(pp.upfront_price or 0), points=pp.cb_points)

        # turn invoice lines into knockout viewmodel blobs and update the context
        for iline in ilines:
            selected_product = Product.objects.filter(code=iline.product)[0]
            if iline.category == 'Premium Items':
                children = ComboLine.objects.filter(parent=selected_product)
                clist = []
                for child in children:
                    ctx['premium']['contents'].append(dict(code=iline.product, quantity=iline.quantity))
                    clist.append(dict(code=child.product.code, quantity=child.quantity))

                ctx['premium']['selected_codes'].append(dict(price=fantastic_pricelist[iline.product]['monthly_each'], code=iline.product, description=selected_product.description, contents=clist, name=selected_product.name))
            elif iline.category == 'Combination Deals':
                children = ComboLine.objects.filter(parent=selected_product)
                clist = []
                for child in children:
                    ctx['combo']['contents'].append(dict(code=iline.product, quantity=iline.quantity))
                    clist.append(dict(code=child.product.code, quantity=child.quantity))

                ctx['combo']['selected_codes'].append(dict(price=fantastic_pricelist[iline.product]['monthly_each'], code=iline.product, description=selected_product.description, contents=clist, name=selected_product.name))
            elif iline.category == 'Services':
                pass
            elif iline.category == 'Rate Drops':
                pass
            elif iline.category == 'Package Customization':
                # create customization lines from the invoice lines of this category
                pass
            else:
                # a-la-carte items use a different paradigm
                partctx = dict(category=iline.category, code=iline.product, name=selected_product.name, price=fantastic_pricelist[iline.product]['monthly_each'], points=fantastic_pricelist[iline.product]['points'])
                cartectx = dict(selected_part=partctx, quantity=iline.quantity)
                ctx['alacarte']['purchase_lines'].append(cartectx)

        # add the things that came from invoice lines to the response context
        response.update(ctx);
        response['package'] = packctx

        # get rid of values the knockout part does not need
        response.pop('done_package', None)
        response.pop('done_premium', None)
        response.pop('done_combo', None)
        response.pop('done_alacarte', None)
        response.pop('done_closing', None)
        response.pop('done_promos', None)

    # handle incoming data
    if request.method == 'POST':
        for key in request.POST:    # request.POST is fucked up when sending JSON
            incoming = loads(key)
            print incoming

        # save agreement state
        agreement.done_premium = incoming.get('premium').get('done')
        agreement.done_combo = incoming.get('combo').get('done')
        agreement.done_alacarte = incoming.get('alacarte').get('done')
        agreement.done_closing = incoming.get('closing').get('done')
        agreement.done_package = incoming.get('package').get('done')
        agreement.done_promos = incoming.get('services_and_promos').get('done')

        # save some of the things we're splitting off
        premiums = incoming.pop('premium', None)
        combos = incoming.pop('combo', None)
        customs = incoming.pop('alacarte', None)
        closers = incoming.pop('closing', None)
        promos = incoming.pop('services_and_promos', None)

        # fix package field if it is the blank package (empty agreement)
        selpkg = incoming.get('package').get('selected_package')
        if selpkg:
            selpkg_code = selpkg.get('code') or ''
        else:
            selpkg_code = ''

        # XXX: might want to do as brian does here and store just a code and not the package object itself
        packages = Package.objects.filter(code=selpkg_code)
        if packages:
            agreement.package = packages[0]

        packs = incoming.pop('package', None)

        # handle invoice lines by first deleting them all and obtaining a price list
        InvoiceLine.objects.filter(agreement=agreement).delete()
        pricelist = get_productprice_list(campaign)

        # pricelist returns a bunch of productprice objects so let's make this easier with something fantastic
        fantastic_pricelist = {}
        for pp in pricelist:
            fantastic_pricelist[pp.product.code] = dict(monthly_each=int(pp.monthly_price or 0), upfront_each=int(pp.upfront_price or 0), pricetable=pp.pricetable.group)

        # now loop through the things that need invoice lines
        # XXX: services and promos (incentives), package customizations, closing
        # this thing coming back from incoming has unicode u'' keys which requires .get()

        # package customization
        for selected in packs.get('customization_lines'):
            pass

        # services and promos
        for selected in promos.get('contents'):
            pass

        for selected in closers.get('contents'):
            pass

        # a-la-carte items
        for selected in customs.get('purchase_lines'):
            # assemble a context
            ilinectx = dict(agreement=agreement, note='', product=selected.get('selected_part').get('code'), category=selected.get('selected_part').get('category'), quantity=int(selected.get('quantity')), pricedate=timezone.now())
            ilinectx.update(fantastic_pricelist[selected.get('selected_part').get('code')])
            ilinectx['monthly_total'] = int(selected.get('quantity')) * int(ilinectx.get('monthly_each') or 0)
            ilinectx['upfront_total'] = int(selected.get('quantity')) * int(ilinectx.get('upfront_each') or 0)

            # create it
            iline = InvoiceLine(**ilinectx)
            iline.save()

        # premium items (actually combos) and combos
        for selected in chain(premiums.get('selected_codes'), combos.get('selected_codes')):
            # obtain the orm product associated with this code
            selected_product = Product.objects.filter(code=selected.get('code'))[0]

            # assemble the pieces into a context
            ilinectx = dict(agreement=agreement, note='', product=selected.get('code'), category=selected.get('category'), quantity=int(selected.get('quantity')), pricedate=timezone.now())
            ilinectx.update(fantastic_pricelist[selected.get('code')])
            ilinectx['monthly_total'] = int(selected.get('quantity')) * int(ilinectx.get('monthly_each') or 0)
            ilinectx['upfront_total'] = int(selected.get('quantity')) * int(ilinectx.get('upfront_each') or 0)

            # actually create this invoice line
            iline = InvoiceLine(**ilinectx)
            iline.save()

            # now handle children of this last line
            for children in selected.get('contents'):
                # obtain this thing's combo line to get its strikeout prices
                child_product = Product.objects.filter(code=children.get('code'))[0]
                cline = ComboLine.objects.filter(parent=selected_product, product=child_product)[0]

                # assemble these pieces
                ichildctx = dict(agreement=agreement, note='', product=children.get('code'), category=children.get('category'), quantity=int(children.get('quantity')), pricedate=timezone.now(), parent=iline)
                ichildctx['monthly_strike'] = int(cline.get('monthly_strike'))
                ichildctx['upfront_strike'] = int(cline.get('upfront_strike'))

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
                'alacarte': {
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

    # a lot of words used to be here but then we wrote pricefunctions.py and got all of it with
    # gen_arrays(), which returns that giant wall of object hierarchy we all know and love... sort of

    # XXX: eventually people should be getting these lists of things from somewhere else by campaign
    return dict(gen_arrays(Campaign.objects.all()[0]), agreement_id=dumps(dict(agreement_id=agreement_id)))


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
