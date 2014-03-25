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
        updater = AgreementUpdater(agreement, None)
        return updater.json_response();

        #jsonable = agreement.as_jsonable()
        #print jsonable

        return JsonResponse(content={'agreement': agreement.as_jsonable()})

    # If we're posting, then get the JSON out of the post data
    post_data = request.POST.get('agreement_update_blob')
    print "*" * 15
    print "THis is what we are savign"
    print post_data
    print "*" * 15
    if not post_data:
        print request.POST
        jsonable = agreement.as_jsonable()
        print jsonable
        return JsonResponse(content={'agreement': jsonable, 'errors': ['There was no POST data.']})

    update_blob = loads(post_data)
    updater = AgreementUpdater(agreement, update_blob)
    updater.update_from_blob(update_blob)

    return updater.json_response()




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
    #applicant_default = {'lname': '', 'phone': '', 'initial': '', 'first_name': '', 'last4': ''}
    address_default = {'city': '', 'state': '', 'address': '', 'zip': '', 'country': ''}

    # create a new agreement
    agreement = Agreement(campaign=campaign, applicant=Applicant(), billing_address=Address(), system_address=Address())

    # now update and save this blank agreement
    #agreement.update_from_dict(dict(billing_address=address_default, system_address=address_default))
    agreement.save()

    # run the other view and pass in the gen_arrays of it and the agreement we just made
    return redirect('draw_container', agreement_id=agreement.id)


@render_to('index.html')
def Index(request):
    if not request.user.is_authenticated():
        return redirect('login')

    if request.GET.get('nav_agreement_id'):
        return redirect('agreement_detail', agreement_id=request.GET.get('nav_agreement_id'))
    return {}
