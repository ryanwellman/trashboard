from annoying.decorators import render_to
from django.shortcuts import redirect
from django.contrib import messages

from _models.agreement import Agreement
from _models.invoiceline import InvoiceLine
from org._models.organization import Organization


@render_to('agreement_detail.html')
def AgreementDetail(request, agreement_id):
    agreement = Agreement.objects.filter(id=agreement_id)

    fields = {
        'id': 'agreement_id',
        'status': 'status',
        'date_updated': 'date_updated',
        'credit_status': 'credit_status',
        'campaign__organization__name': 'organization_name',
        'applicant_id__first_name': 'applicant_first_name',
        'applicant_id__last_name': 'applicant_last_name',
        'applicant_id__credit_file__beacon': 'applicant_beacon',
        'applicant_id__credit_file__transaction_id': 'applicant_transaction_id',
        'coapplicant_id__first_name': 'coapplicant_first_name',
        'coapplicant_id__last_name': 'coapplicant_last_name',
        'coapplicant_id__credit_file__beacon': 'coapplicant_beacon',
        'coapplicant_id__credit_file__transaction_id': 'coapplicant_transaction_id',
        'email': 'email',
        'install_method': 'install_method',
        'property_type': 'property_type',
        'floorplan': 'floorplan'
    }

    ag_summary = agreement.values(*fields.keys())

    lines = InvoiceLine.objects.filter(agreement_id=agreement_id).values('product_type', 'product', 'quantity')
    print "lines", lines
    ag_lines = {}
    closers = []
    products = []
    for l in lines:
        if l['product_type'] == "Package":
            ag_lines['package'] = l['product']
        if l['product_type'] == "Monitoring":
            ag_lines['monitoring'] = l['product']
        if l['product_type'] == "Shipping":
            ag_lines['shipping'] = l['product']
        if l['product_type'] == "Closer":
            closers.append(l['product'])
        if l['product_type'] == "Part":
            product = {}
            product['part'] = l['product']
            product['quantity'] = l['quantity']
            products.append(product)
    ag_lines['closers'] = closers
    ag_lines['products'] = products

    print "ag", ag_lines
    if request.method == 'POST':
        if "approve_credit" in request.POST:
            print "approve the credit yo"
            print "agreement", agreement_id
            agreement = Agreement.objects.get(id=agreement_id)
            agreement.credit_status = 'APPROVED'
            agreement.credit_override = 'APPROVED'
            agreement.save()
            # messages.success(request, "Credit for Agreement {0} has been approved".format(agreement_id))
            return redirect('agreement_detail', agreement_id=agreement_id)
        if "decline_credit" in request.POST:
            print "you've been declined fool"
    return dict(ag_summary=ag_summary,
                ag_lines=ag_lines)


@render_to('credit_review.html')
def CreditReview(request):
    if request.GET.get('nav_agreement_id'):
        return redirect('agreement_detail', agreement_id=request.GET.get('nav_agreement_id'))

    if request.method == 'POST':
        if "approve_credit" in request.POST:
            approve_agreement = request.POST.get('agreement_id')
            agreement = Agreement.objects.get(id=approve_agreement)
            agreement.credit_override = 'APPROVED'
            agreement.save()
            return redirect('credit_review')
        if "decline_credit" in request.POST:
            decline_agreement = request.POST.get('agreement_id')
            agreement = Agreement.objects.get(id=decline_agreement)
            agreement.credit_override = 'DCS'
            agreement.save()
            return redirect('credit_review')

        return redirect('credit_review')


    agreements = Agreement.objects.filter(status__in=['DRAFT', ''])
    # Re-review a specific id
    if request.GET.get('agreement_id'):
        agreements = agreements.filter(pk=request.GET.get('agreement_id'))
        print "agreements", agreements
    else:
        # Review anything that isn't overridden already.
        agreements = agreements.filter(credit_status__in=['REVIEW', 'NO HIT'], credit_override__isnull=True)

    fields = {
        'id' : 'agreement_id',
        'date_updated': 'date_updated',
        'credit_status': 'credit_status',
        'credit_override': 'credit_override',
        'campaign__organization__name': 'organization_name',
        'applicant_id__first_name': 'applicant_first_name',
        'applicant_id__last_name': 'applicant_last_name',
        'applicant_id__credit_file__beacon': 'applicant_beacon',
        'applicant_id__credit_file__transaction_id': 'applicant_transaction_id',
        'coapplicant_id__first_name': 'coapplicant_first_name',
        'coapplicant_id__last_name': 'coapplicant_last_name',
        'coapplicant_id__credit_file__beacon': 'coapplicant_beacon',
        'coapplicant_id__credit_file__transaction_id': 'coapplicant_transaction_id',
    }
    pending_credit = agreements.values(*fields.keys())
    pending_credit = [
        {
            new_key: row[key]
            for key, new_key in fields.iteritems()
        }
        for row in pending_credit
    ]
    print pending_credit


    return dict(pending_credit=pending_credit)


@render_to('bypass.html')
def BypassUpfrontAuthorization(request):
    if request.GET.get('nav_agreement_id'):
        return redirect('agreement_detail', agreement_id=request.GET.get('nav_agreement_id'))

    qs = Agreement.objects.filter(status='PUBLISHED', bypass_upfront_authorization=False)
    published = qs.values('id', 'date_updated', 'applicant_id__first_name', 'applicant_id__last_name', 'campaign__organization__name')

    if request.POST:
        bypass_agreement = request.POST.get('agreement_id')
        agreement = Agreement.objects.get(id=bypass_agreement)
        agreement.bypass_upfront_authorization = True
        agreement.save()
        return redirect('bypass')

    return dict(published=published)


@render_to('manage.html')
def ManageProviders(request):
    if request.GET.get('nav_agreement_id'):
        print "agreement", request.GET.get('nav_agreement_id')
        return redirect('agreement_detail', agreement_id=request.GET.get('nav_agreement_id'))

    orgs = Organization.objects.all()

    return dict(orgs=orgs)
