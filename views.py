# import built-ins
from json import dumps, loads
from itertools import chain
from collections import defaultdict

# import 3rd-party modules
from annoying.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404, redirect
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# import from self (models)
from agreement.models import *
from pricefunctions import *
from handy import intor
from handy.jsonstuff import dumps
from handy.controller import JsonResponse

from agreement.agreement_updater import AgreementUpdater

@csrf_exempt
def dyn_json(request, agreement_id=None):
    """
    reads or updates an Agreement and returns it to the caller as json

    XXX: in several places the knockout accepts only one price for an item which for now is monthly_price
    XXX: this could be refactored as a controller with multiple helper methods
    """

    # attempts to get or set a specific agreement
    agreement = None
    response = None

    # handle obtaining an agreement object and fail if there is no id present
    if agreement_id:
        agreement = get_object_or_404(Agreement.objects.all(), pk=agreement_id)
    else:
        raise Agreement.DoesNotExist

    # handle outgoing data
    if request.method == 'GET':
        jsonable = agreement.as_jsonable()
        print jsonable

        return JsonResponse(content={'agreement': agreement.as_jsonable()})

    # If we're posting, then get the JSON out of the post data
    post_data = request.POST.get('agreement_update_blob')
    if not post_data:
        print request.POST
        jsonable = agreement.as_jsonable()
        print jsonable
        return JsonResponse(content={'agreement': jsonable, 'errors': ['There was no POST data.']})

    update_blob = loads(post_data)
    updater = AgreementUpdater(agreement, update_blob)
    updater.update_from_blob(update_blob)

    return updater.json_response()



    jsonable = agreement.as_jsonable()
    print jsonable


    if False:

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
                        'selected_promos': [],
                        'selected_services': [],
                        'done': agreement.done_promos,
                    },
                    'review': {
                        'contents': [],
                    },
                }

        # package is its own can of worms
        if agreement.package:
            code = agreement.package.code
        else:
            code = ''

        # create a context again
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
        pricelist = agreement.campaign.get_product_prices()
        #pricelist = get_productprice_list(agreement.campaign)
        fantastic_pricelist = {}
        for pp in pricelist:
            fantastic_pricelist[pp.product.code] = dict(monthly_each=int(pp.monthly_price or 0), upfront_each=int(pp.upfront_price or 0), points=pp.cb_points)

        # turn invoice lines into knockout viewmodel blobs and update the context
        # XXX: use product type here rather than the categories?
        for iline in ilines:
            # place all of these things into review as serialized invoice lines
            ctx['review']['contents'].append(iline.serialize(ignore=['agreement', 'pricetable']))

            # skip combo children invoice lines; they will cascade from the parents
            if iline.parent and iline.category not in ['Services', 'Incentives']:
                continue

            # XXX: this gets around the packages being fake products in the invoice lines
            # XXX: probably going to add duped products for the packages anyway so that
            #      they have prices from the price lists so we can use that here
            if iline.category != 'Package':
                selected_product = Product.objects.get(code=iline.product)
            else:
                selected_product = Package.objects.get(code=iline.product)

            if iline.category == 'Premium Items':
                children = ComboLine.objects.filter(parent=selected_product)
                clist = []
                for child in children:
                    ctx['premium']['contents'].append(dict(code=child.product.code, quantity=child.quantity))
                    clist.append(dict(code=child.product.code, quantity=child.quantity))

                ctx['premium']['selected_codes'].append(dict(price=fantastic_pricelist[iline.product]['monthly_each'], code=iline.product, description=selected_product.description, contents=clist, name=selected_product.name))
            elif iline.category == 'Combos':
                children = ComboLine.objects.filter(parent=selected_product)
                clist = []
                for child in children:
                    ctx['combo']['contents'].append(dict(code=child.product.code, quantity=child.quantity))
                    clist.append(dict(code=child.product.code, quantity=child.quantity))

                ctx['combo']['selected_codes'].append(dict(price=fantastic_pricelist[iline.product]['monthly_each'], code=iline.product, description=selected_product.description, contents=clist, name=selected_product.name))
            elif iline.category == 'Rate Drops':
                # these guys look exactly like premiums and combos but with no contents
                ctx['closing']['selected_codes'].append(dict(price=fantastic_pricelist[iline.product]['monthly_each'], code=iline.product, description=selected_product.description, name=selected_product.name))
            elif iline.category == 'Package':
                # obtain this package's actual contents and put its name in packctx
                pkgcontents = {}
                packctx['selected_package']['contents'] = []
                packctx['selected_package']['name'] = agreement.package.name

                # go through the contents and update packctx and pkgcontents while adding up total cb points for this package
                cbp = 0
                for pp in agreement.package.contents.all():
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
            elif iline.category == 'Services':
                # services and incentives aren't mutable by the user
                ctx['services_and_promos']['selected_services'].append(iline.product)
            elif iline.category == 'Incentives':
                ctx['services_and_promos']['selected_promos'].append(iline.product)
            elif iline.category == 'Shipping':
                response['shipping'] = iline.product # XXX: do something about this being shitty
            elif iline.category == 'Monitoring':
                response['monitoring'] = iline.product
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
        agreement.date_updated = timezone.now()
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
        try:
            agreement.package = Package.objects.get(code=selpkg_code)
        except Package.DoesNotExist: # ugly
            pass

        packs = incoming.pop('package', None)

        # from this point on we need to have a saved agreement to do anything

        # handle invoice lines by first deleting them all and obtaining a price list
        InvoiceLine.objects.filter(agreement=agreement).delete()

        pricelist = agreement.campaign.get_product_prices()
        #get_productprice_list(agreement.campaign)

        # obtain the list of active price tables
        activepts = agreement.campaign.get_pricetables()
        #activepts = [obj['pt'] for obj in get_zorders(agreement.campaign)]

        # pricelist returns a bunch of productprice objects so let's make this easier with something fantastic
        fantastic_pricelist = {}
        for pp in pricelist:
            fantastic_pricelist[pp.product.code] = dict(monthly_each=int(pp.monthly_price or 0), upfront_each=int(pp.upfront_price or 0), pricetable=pp.pricetable.name)

        # now loop through the things that need invoice lines
        # XXX: services and promos (incentives) closing
        # this thing coming back from incoming has unicode u'' keys which requires .get()

        # package customization
        # get the contents of the package as a hash of codes:quantities
        pkgcontents = {}
        if agreement.package:
            for pc in agreement.package.contents.all():
                pkgcontents[pc.included_product_id] = pc.quantity

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

        # closers
        for selected in closers.get('selected_codes', []):
            # obtain the orm product
            selected_product = Product.objects.get(code=selected.get('code'))

            # assemble a context
            # XXX: no quantities are associated in the form for this object so they are 1
            ilinectx = dict(agreement=agreement, note='', product=selected.get('code'), category=selected_product.category, quantity=1, pricedate=timezone.now())
            # XXX: no prices yet

            # create it
            iline = InvoiceLine(**ilinectx)
            iline.save()

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
        for selected in combos.get('selected_codes'):
            # obtain the orm product associated with this code
            selected_product = Product.objects.get(code=selected.get('code'))

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
                child_product = Product.objects.get(code=children.get('code'))

                # obtain this thing's combo line to get its strikeout prices
                cline = ComboLine.objects.get(parent=selected_product, product=child_product)

                # assemble these pieces
                ichildctx = dict(agreement=agreement, note='', product=children.get('code'), category=child_product.category, quantity=int(children.get('quantity')), pricedate=timezone.now(), parent=iline)
                ichildctx['monthly_strike'] = int(cline.monthly_strike or 0)
                ichildctx['upfront_strike'] = int(cline.upfront_strike or 0)

                # actually create it
                ichild = InvoiceLine(**ichildctx)
                ichild.save()

        # services and promos
        # lasciate ogne speranza, voi ch'intrate

        # this is recalculated each time an agreement blob is sent to the json handler
        # XXX: detect changes to this and skip unchanged?
        # XXX: way too many round trips to the database
        # XXX: way too many loops
        # XXX: ugly ugly ugly ugly ugly ugly ugly ugly ugly ugly ugly ugly ugly ugly ugly ugly

        # key all the invoice lines now in this agreement to their product codes
        # they were blanked out before dealing with the products so that's all that should be there
        codedlines = {iline.product: iline for iline in InvoiceLine.objects.filter(agreement=agreement)}

        # get the actual product objects that are in the coded lines for these queries since invoice lines only have codes
        ag_contents = Product.objects.filter(code__in=codedlines.keys())

        # ask the orm for the require lines of the codedlines keys (the product keys) that are active
        # these are the things that require other items to be purchased (services for sure)
        requires = RequiresLine.objects.filter(parent__in=ag_contents, pricetable__in=activepts)

        # ask the orm for all the require lines in the current pricetable set with no children (for sure an incentive, requires nothing)
        # these require no additional consistency checking
        easypromos = RequiresLine.objects.filter(child=None, pricetable__in=activepts)

        # ask the orm for all the require lines in the current pricetable set whose children are items in this agreement
        # these are ones that need to be checked for containing all of their children and for being an incentive
        hardpromos = RequiresLine.objects.filter(child__in=ag_contents, pricetable__in=activepts)

        # at this point the union of the above 3 lists contains all the services and promos that
        # might match this particular agreement...
        for rline in chain(requires, easypromos):
            # test this require line
            if rline.parent.category == 'Incentives':
                # handle incentives (promos)
                ilinectx = dict(agreement=agreement, note='', product=rline.parent.code, category=rline.parent.category, quantity=1, pricedate=timezone.now())
                if rline.child: # this has a requirement (should not execute ever)
                     ilinectx['parent'] = codedlines[iline.child.code]
                ilinectx.update(fantastic_pricelist[rline.parent.code])
            else:
                # handle services
                ilinectx = dict(agreement=agreement, note='', product=rline.child.code, category=rline.child.category, quantity=rline.quantity, pricedate=timezone.now(), mandatory=True)
                ilinectx.update(fantastic_pricelist[rline.child.code])

            # actually make this thing
            iline = InvoiceLine(**ilinectx)
            iline.save()

        # ...however, hardpromos contains possibly incomplete promotions so deal with that now
        # counting the number of require lines for the codes in question and making sure the count in hardpromos
        # matches should work since these values are coming from the database

        # sort hardpromos (a list) by parent codes so we have consecutive requirements for whatever incentive
        hardpromos = sorted(hardpromos, key=lambda i: i.parent.code)

        cached_incentive, cached_rlines, seen_rlines = object(), [], 0 # XXX: could this be a defaultdict?
        # this version of the loop makes sure promos that have requirements all get counted
        # it also depends on the list being sorted by incentive as above
        for rline in hardpromos:
            # test this require line
            if rline.parent.category == 'Incentives':
                # compare to cache and change if it changed
                if rline.parent != cached_incentive:
                    cached_incentive = rline.parent
                    cached_rlines = RequiresLine.objects.filter(parent=rline.parent)
                    seen_rlines = 0

                seen_rlines += 1

                # only create an invoice line if this thing matches counts
                if seen_rlines == len(cached_rlines):
                    ilinectx = dict(agreement=agreement, note='', product=rline.parent.code, category=rline.parent.category, quantity=1, pricedate=timezone.now())
                    ilinects['parent'] = codedlines[rline.parent.code] # last one
                    ilinectx.update(fantastic_pricelist[rline.parent.code])
                    iline = InvoiceLine(**ilinectx)
                    iline.save()
            else:
                # this a product in our agreement that is required by some other product so skip it
                continue

            # create the invoice line
            iline = InvoiceLine(**ilinectx)
            iline.save()

        # create some invoice lines for shipping and monitoring here
        # XXX: neither of these are in the products yet so they have no price information
        if agreement.monitoring:
            # XXX: again just one for quantity here
            ilinectx = dict(agreement=agreement, note='', product=agreement.monitoring, category='Monitoring', quantity=1, pricedate=timezone.now())
            iline = InvoiceLine(**ilinectx)
            iline.save()

        if agreement.shipping:
            ilinectx = dict(agreement=agreement, note='', product=agreement.shipping, category='Shipping', quantity=1, pricedate=timezone.now())
            iline = InvoiceLine(**ilinectx)
            iline.save()

        # update agreement with values from incoming, finally
        agreement.update_from_dict(incoming)

        # create a response
        response = agreement.serialize(ignore=['campaign'])
        print response

    if request.method == 'PUT':
        pass

    if request.method == 'DELETE':
        pass

    return JsonResponse(content=response)
    return SerializeOrRedirect(reverse('draw_container'), response)


def create_and_redirect(request):
    """
    creates a new, blank agreement with the parameters from whatever campaign was passed in
    then it redirects you to that agreement by its id and passes in the output from gen_arrays
    """

    # attempt to capture the campaign id from the url
    campaign_id = request.GET.get('campaign_id', None)
    assert campaign_id is not None

    # obtain the campaign object
    try:
        campaign = Campaign.objects.get(campaign_id=campaign_id)
    except Campaign.DoesNotExist:
        campaign = Campaign.objects.all()[0] # XXX: bad

    # some defaults
    applicant_default = {'lname': '', 'phone': '', 'initial': '', 'fname': '', 'last4': ''}
    address_default = {'city': '', 'state': '', 'address': '', 'zip': '', 'country': ''}

    # create a new agreement
    agreement = Agreement(campaign=campaign, applicant=Applicant(), billing_address=Address(), system_address=Address())

    # now update and save this blank agreement
    agreement.update_from_dict(dict(applicant=applicant_default, billing_address=address_default, system_address=address_default))

    # run the other view and pass in the gen_arrays of it and the agreement we just made
    return redirect('draw_container', agreement_id=agreement.id)