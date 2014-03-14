from annoying.decorators import render_to
from _models.agreement import Agreement
from django.shortcuts import redirect


@render_to('index.html')
def Index(request):
    return {}


@render_to('credit_review.html')
def CreditReview(request):
    pending_credit = Agreement.objects.values('id', 'date_updated', 'applicant_id__first_name', 'applicant_id__last_name')

    if "approve_credit" in request.POST:
        approve_agreement = request.POST.get('agreement_id')
        agreement = Agreement.objects.get(id=approve_agreement)
        agreement.credit_override = 'APPROVED'
        agreement.save()
        return redirect('credit_review')
    if "decline_credit" in request.POST:
        decline_agreement = request.POST.get('agreement_id')
        agreement = Agreement.objects.get(id=decline_agreement)
        agreement.credit_override = 'DECLINED'
        agreement.save()
        return redirect('credit_review')

    return dict(pending_credit=pending_credit)


@render_to('bypass.html')
def BypassUpfrontAuthorization(request):
    published = Agreement.objects.values('id', 'date_updated', 'applicant_id__first_name', 'applicant_id__last_name')

    if request.POST:
        print "let's bypass this shit"
        bypass_agreement = request.POST.get('agreement_id')
        agreement = Agreement.objects.get(id=bypass_agreement)
        agreement.bypass_upfront_authorization = True
        agreement.save()
        return redirect('bypass')

    return dict(published=published)
