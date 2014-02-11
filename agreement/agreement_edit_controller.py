from handy.controller import GenericController
from handy import intor
from handy.jsonstuff import dumps
from agreement.models import Agreement, Product
from pricefunctions import get_global_context
from django.shortcuts import get_object_or_404, redirect

class AgreementEditController(GenericController):
    def template_name(self):
        return 'container.html'

    def fetch_objects(self):
        self.agreement_id = intor(self.agreement_id)
        self.agreement = get_object_or_404(Agreement.objects.all(), pk=self.agreement_id)

        self.campaign = self.agreement.campaign if self.agreement else None


    def dispatch(self, request):

        """
        renders an agreement form container to the caller along with its parts
        """
        # no agreement id means someone tried to access the root-level site
        # this means there's no campaign so the view will fail below

        self.set_global_context()


        return self.render()

    def set_global_context(self):
        # Get the valid prices
        self.products = Product.get_all_products()
        self.pricelist = self.campaign.get_product_prices()


        # Translate to json.
        self.products_json = dumps({code: p.as_jsonable() for code, p in self.products.iteritems()})
        self.pricelist_json = dumps({code: pp.as_jsonable() for code, pp in self.pricelist.iteritems()})


class AgreementJsonController(GenericController):
    def render():
        return JsonResponse(dict(
            agreement=self.agreement.as_jsonable(),
            errors=self.errors
        ))

    def fetch_objects(self):
        self.agreement_id = intor(self.agreement_id)
        self.agreement = get_object_or_404(Agreement.objects.all(), pk=self.agreement_id)

        self.campaign = self.agreement.campaign if self.agreement else None

        self.errors = []

    def dispatch(request):
        if request.method == 'POST':
            incoming_blob = request.POST.get('update_agreement_blob')
            incoming = loads(incoming_blob)

            self.errors = agreement.update_with_blob(incoming_blob) or []

        return self.render()



