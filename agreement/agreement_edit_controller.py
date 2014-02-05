from handy.controller import GenericController
from handy import intor
from handy.jsonstuff import dumps
from agreement.models import Agreement
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
        pricelist = self.campaign.get_product_prices()

        # index pricelist by product_id
        pricelist = {pp.product_id: pp for pp in pricelist}

        products = []

        # Get all Package objects with type 'package', all Part objects with type 'part',
        # etc etc.  (Already concreted)
        from agreement.models import __typemap__
        for product_type, product_kls in __typemap__.iteritems():
            products.extend(list(product_kls.objects.filter(product_type=product_type)))

        # Index all the products.
        products = {p.code: p for p in products}

        self.products = products
        self.pricelist = pricelist

        # Translate to json.
        self.products_json = dumps({code: p.as_jsonable() for code, p in products.iteritems()})
        self.pricelist_json = dumps({code: pp.as_jsonable() for code, pp in pricelist.iteritems()})
