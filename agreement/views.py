from annoying.decorators import render_to
from _models.agreement import Agreement
from django.shortcuts import redirect


@render_to('credit_review.html')
def CreditReview(request):

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
    qs = Agreement.objects.filter(status='PUBLISHED', bypass_upfront_authorization=False)
    published = qs.values('id', 'date_updated', 'applicant_id__first_name', 'applicant_id__last_name', 'campaign__organization__name')

    if request.POST:
        bypass_agreement = request.POST.get('agreement_id')
        agreement = Agreement.objects.get(id=bypass_agreement)
        agreement.bypass_upfront_authorization = True
        agreement.save()
        return redirect('bypass')

    return dict(published=published)
