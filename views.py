# import built-ins
from json import dumps, loads
from itertools import chain
from collections import defaultdict

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
    XXX: in several places the knockout accepts only one price for an item which for now is monthly_price
    """

    # attempts to get or set a specific agreement
    agreement = None
    response = None
    campaign = Campaign.objects.all()[0]

    # handle obtaining an agreement object
    if agreement_id:
        # user wants a specific agreement
        agreement = get_object_or_404(Agreement.objects.all(), pk=agreement_id)
    else:
        # make a new agreement with non-optional blank child models included (foreign keys)
        agreement = Agreement(campaign=campaign, applicant=Applicant(), billing_address=Address(), system_address=Address())

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
        if agreement.package:
            code = agreement.package.code
        else:
            code = ''

        # create a context again
        # XXX: make this load properly in knockout when these values are fed in
        packctx =   {
                    'selected_package': {
                        'code': code,
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
            # skip children invoice lines; they will cascade from the parents
            if iline.parent:
                continue

            # XXX: this gets around the packages being fake products in the invoice lines
            if iline.category != 'Package':
                selected_product = Product.objects.filter(code=iline.product)[0]
            else:
                selected_product = Package.objects.filter(code=iline.product)[0]

            if iline.category == 'Premium Items':
                children = ComboLine.objects.filter(parent=selected_product)
                clist = []
                for child in children:
                    ctx['premium']['contents'].append(dict(code=child.product.code, quantity=child.quantity))
                    clist.append(dict(code=child.product.code, quantity=child.quantity))

                ctx['premium']['selected_codes'].append(dict(price=fantastic_pricelist[iline.product]['monthly_each'], code=iline.product, description=selected_product.description, contents=clist, name=selected_product.name))
            elif iline.category == 'Combination Deals':
                children = ComboLine.objects.filter(parent=selected_product)
                clist = []
                for child in children:
                    ctx['combo']['contents'].append(dict(code=child.product.code, quantity=child.quantity))
                    clist.append(dict(code=child.product.code, quantity=child.quantity))

                ctx['combo']['selected_codes'].append(dict(price=fantastic_pricelist[iline.product]['monthly_each'], code=iline.product, description=selected_product.description, contents=clist, name=selected_product.name))
            elif iline.category == 'Services':
                pass
            elif iline.category == 'Rate Drops':
                pass
            elif iline.category == 'Package':
                # obtain this package's actual contents and put its name in packctx
                pkgcontents = {}
                packctx['selected_package']['contents'] = []
                packctx['selected_package']['name'] = agreement.package.name

                # go through the contents and update packctx and pkgcontents while adding up total cb points for this package
                cbp = 0
                for pp in agreement.package.pkgproduct_set.all():
                    pkgcontents[pp.product.code] = pp.quantity
                    packctx['selected_package']['contents'].append(dict(code=pp.product.code, quantity=pp.quantity, part=dict(category=pp.product.category, price=fantastic_pricelist[pp.product.code]['monthly_each'], points=fantastic_pricelist[pp.product.code]['points'], name=pp.product.name, code=pp.product.code)))
                    cbp += int(fantastic_pricelist[pp.product.code]['points']) * pp.quantity

                # need to take children from the invoice lines this time
                children = InvoiceLine.objects.filter(parent=iline)

                changes, clist = (defaultdict(bool), [])
                for child in children:
                    # attempt to figure out if this package has been customized
                    changes[child.product] = (pkgcontents.get(child.product, None) == child.quantity) # only true if it hasn't changed and exists in pkgcontents

                    # subtract points from the cb point total above; what's left is the balance
                    cbp -= int(fantastic_pricelist[child.product]['points']) * child.quantity

                    # now put this dict into the list of customized parts
                    # XXX: this following line could be cached somewhere else
                    child_product = Product.objects.filter(code=child.product)[0]
                    clist.append(dict(code=child.product, quantity=child.quantity, part=dict(category=child_product.category, price=fantastic_pricelist[child.product]['monthly_each'], points=fantastic_pricelist[child.product]['points'], name=child_product.name, code=child.product)))

                # put changes into packctx
                packctx['changed_contents'] = not reduce(lambda i, j: i and j, changes.values()) # a false here will make the whole thing false 
                packctx['cb_balance'] = cbp
                packctx['updated_contents'] = clist

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
        agreement.done_premium = incoming.get('premium').get('done', False)
        agreement.done_combo = incoming.get('combo').get('done', False)
        agreement.done_alacarte = incoming.get('alacarte').get('done', False)
        agreement.done_closing = incoming.get('closing').get('done', False)
        agreement.done_package = incoming.get('package').get('done', False)
        agreement.done_promos = incoming.get('services_and_promos').get('done', False)

        # save some of the things we're splitting off
        premiums = incoming.pop('premium', None)
        combos = incoming.pop('combo', None)
        customs = incoming.pop('alacarte', None)
        closers = incoming.pop('closing', None)
        promos = incoming.pop('services_and_promos', None)

        # fix package field if it is none (blank agreement)
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

        # from this point on we need to have a saved agreement to do anything
        # XXX: remove ugly hax
        if not agreement_id: # if the id is present we have something that's been saved
            # define some defaults
            applicant_default = {'lname': '', 'phone': '', 'initial': '', 'fname': ''}
            address_default = {'city': '', 'state': '', 'address': '', 'zip': '', 'country': ''}

            # populate the agreement and save it
            agreement.update_from_dict(dict(applicant=incoming.get('applicant', applicant_default), billing_address=incoming.get('billing_address', address_default), system_address=incoming.get('system_address', address_default)))

        # handle invoice lines by first deleting them all and obtaining a price list
        InvoiceLine.objects.filter(agreement=agreement).delete()
        pricelist = get_productprice_list(campaign)

        # pricelist returns a bunch of productprice objects so let's make this easier with something fantastic
        fantastic_pricelist = {}
        for pp in pricelist:
            fantastic_pricelist[pp.product.code] = dict(monthly_each=int(pp.monthly_price or 0), upfront_each=int(pp.upfront_price or 0), pricetable=pp.pricetable.group)

        # now loop through the things that need invoice lines
        # XXX: services and promos (incentives) closing
        # this thing coming back from incoming has unicode u'' keys which requires .get()

        # package customization
        # get the contents of the package as a hash of codes:quantities
        pkgcontents = {}
        if agreement.package:
            for pp in agreement.package.pkgproduct_set.all():
                pkgcontents[pp.product.code] = pp.quantity

            # create a parent invoice line for the package contents
            # this context is constructed a little differently than ones with an actual product;
            # the product and category are both effectively fake because they are the package's data instead
            ilinectx = dict(agreement=agreement, note='', product=agreement.package.code, category='Package', quantity=1, pricedate=timezone.now())
            pkgiline = InvoiceLine(**ilinectx)
            pkgiline.save()

        # now apply the deltas
        for selected in packs.get('customization_deltas', []):
            # XXX: i think the javascript part gets rid of zero deltas itself
            if selected.get('delta'):
                try:
                    pkgcontents[selected.get('code')] += selected.get('delta')
                except KeyError, e:
                    pkgcontents[selected.get('code')] = selected.get('delta')

        # remove negative and zero results
        pkgcontents = dict((k, v) for k, v in pkgcontents.iteritems() if v > 0)

        # now go through all the contents and add the appropriate invoice lines to the parent:
        #   + child invoice lines representing the customized contents with currently no pricing information
        for child, quantity in pkgcontents.iteritems():
            # XXX: fake category "package customization"
            ilinectx = dict(agreement=agreement, note='', product=child, category='Package Customization', quantity=quantity, pricedate=timezone.now(), parent=pkgiline)

            # actually make this thing
            iline = InvoiceLine(**ilinectx)
            iline.save()

        # services and promos
        for selected in promos.get('contents', []):
            pass

        for selected in closers.get('contents', []):
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
            # XXX: these things don't have a quantity associated with them right now it's just 1
            ilinectx = dict(agreement=agreement, note='', product=selected.get('code'), category=selected_product.category, quantity=1, pricedate=timezone.now())
            ilinectx.update(fantastic_pricelist[selected.get('code')])
            ilinectx['monthly_total'] = int(1) * int(ilinectx.get('monthly_each') or 0) # XXX: add quantity here
            ilinectx['upfront_total'] = int(1) * int(ilinectx.get('upfront_each') or 0)

            # actually create this invoice line
            iline = InvoiceLine(**ilinectx)
            iline.save()

            # now handle children of this last line
            for children in selected.get('contents'):
                # need this to get the combo line and the category
                child_product = Product.objects.filter(code=children.get('code'))[0]

                # obtain this thing's combo line to get its strikeout prices
                cline = ComboLine.objects.filter(parent=selected_product, product=child_product)[0]

                # assemble these pieces
                ichildctx = dict(agreement=agreement, note='', product=children.get('code'), category=child_product.category, quantity=int(children.get('quantity')), pricedate=timezone.now(), parent=iline)
                ichildctx['monthly_strike'] = int(cline.monthly_strike or 0)
                ichildctx['upfront_strike'] = int(cline.upfront_strike or 0)

                # actually create it
                ichild = InvoiceLine(**ichildctx)
                ichild.save()

        # update agreement with values from incoming
        agreement.update_from_dict(incoming)

        # create a response
        response = agreement.serialize(ignore=['campaign'])
        print response

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
