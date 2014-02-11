from django.db import models
from datetime import datetime
from django.utils import timezone
from ..uas import Serializable, Updatable
from applicant import Applicant
from address import Address
from campaign import Campaign
from package import Package


class Agreement(Updatable):
    """
    represents an agreement by a customer to buy our products

    this particular version of Agreement is a shim for the actual Agreement
    which exists in dashboard and may or may not be compatible with this one

    general field reference:
        campaign: who gets paid commission
        applicants: whose credit is going to be run
        addresses: where to bill and where the alarm is
        pricetable_date: what day's prices should be used
        email: how to contact the applicants about this agreement
        approved: what was their credit score like
        package: what box do we use
        shipping: who gets paid to transport the package
        monitoring: who gets paid to watch this system
        floorplan: what shape is the target address
        promo_code: just one for now!

    this field is updatable from a json-like blob
    """

    campaign = models.ForeignKey(Campaign)
    applicant = models.ForeignKey(Applicant, related_name='main_applicant')
    coapplicant = models.ForeignKey(Applicant, related_name='co_applicant', blank=True, null=True)
    billing_address = models.ForeignKey(Address, related_name='billing')
    system_address =models.ForeignKey(Address, related_name='system')
    pricetable_date = models.DateTimeField(default=timezone.now) # automatically timestamped on creation
    date_updated = models.DateTimeField(default=timezone.now) # update when updated
    email = models.CharField(max_length=75)
    approved = models.CharField(max_length=20)
    package = models.ForeignKey(Package, related_name='package', blank=True, null=True) # now nullable
    shipping = models.CharField(max_length=20)
    monitoring = models.CharField(max_length=20)
    floorplan = models.CharField(max_length=20)
    promo_code = models.CharField(max_length=20)
    done_premium = models.BooleanField(default=False)
    done_combo = models.BooleanField(default=False)
    done_alacarte = models.BooleanField(default=False)
    done_closing = models.BooleanField(default=False)
    done_package = models.BooleanField(default=False)
    done_promos = models.BooleanField(default=False)

    def __unicode__(self):
        if not self.id:
            id_display = u'Unsaved'
        else:
            id_display = unicode(self.id)

        fields = [id_display, self.approved]
        try:
            fields.append(self.campaign)
            fields.append(self.applicant)
            fields.append(self.package)
            fields.append(self.billing_address)
        except ObjectDoesNotExist:
            pass
        return u','.join([unicode(f) for f in fields])

    def as_jsonable(self):
        jsonable = dict()
        for field in ('campaign', 'applicant', 'coapplicant',
                      'billing_address', 'system_address'):
            obj = getattr(self, field)
            jsonable[field] = obj.as_jsonable() if obj else None

        for field in ('pricetable_date', 'date_updated', 'email', 'approved', 'promo_code'):
            jsonable[field] = getattr(self, field)

        jsonable['invoice_lines'] = [il.as_jsonable() for il in self.invoice_lines.all()]


        return jsonable

    def update_from_blob(self, update_blob):
        # this is where the vast majority of the magic is going to happen.
        errors = []

        if 'applicant' in update_blob:
            # We are assigning applicant.  If we don't have one already, make it.
            target_applicant = self.applicant
            if not target_applicant:
                target_applicant = Applicant()

            errors.extend(
                target_applicant.update_from_blob(update_blob['applicant'])
            )
            target_applicant.save()
            self.applicant = target_applicant # Put it back on myself.

        if 'coapplicant' in update_blob:
            # We are assigning applicant.  If we don't have one already, make it.
            target_applicant = self.coapplicant
            if not target_applicant:
                target_applicant = Applicant()

            errors.extend(
                target_applicant.update_from_blob(update_blob['coapplicant'])
            )
            target_applicant.save()
            self.coapplicant = target_applicant # Put it back on myself.

        if 'system_address' in update_blob:
            target_address = self.system_address
            if not target_address:
                target_address = Address()

            errors.extend(
                target_address.update_from_blob(update_blob['system_address'])
            )
            target_address.save()
            self.system_address = target_address

        if 'invoice_lines' in update_blob:
            errors.extend(
                self.update_invoice_lines(update_blob['invoice_lines'])
            )


    def update_invoice_lines(self, new_invoice_lines):
        # begin building a list of errors to return.
        errors = []

        # The incoming invoice lines should look like:
        '''
        [{
            'code': 'COPPER',
            'quantity': 1
        }, ...]
        '''
        # Nothing else is needed from the interface side, since it'll synchronize itself.
        # We're also only really looking at the top-level invoice lines.  Anything beneath that
        # will be added/removed as appropriate, probably at the very last step.

        # we're going to need a bunch of stuff from inventory to start.
        # Each of these is a dictionary by product code.
        products = Product.get_all_products()
        pricelist = self.campaign.get_product_prices()


        # coerce new_invoice_lines into object-likes so that this code isn't a mishmash
        # of [item] and .attribute access.
        class IL(object):
            def __init__(self, line):
                self.code = line.get('code')
                self.quantity = intor(line.get('quantity'))
                self.product = products.get(self.code)

                if not self.code or self.quantity is None:
                    errors.append('Invalid invoiceline update: %r' % (line,))
                elif not self.product:
                    errors.append('The product %s could not be found.' % line.code)
                elif not self.code in pricelist:
                    errors.append('The product %s is not available for the campaign %s' % self.campaign_id)

        new_invoice_lines = [IL(line) for line in new_invoice_lines]
        # Index them
        new_invoice_lines = {line.code: line for line in new_invoice_lines}

        # The constructor will have grabbed the products.  If we had any errors now, stop.
        if errors:
            return errors


        # Next get every existing invoice line.
        existing_lines = list(self.invoice_lines.all())
        # separate out the child lines, and index the top ones.
        child_lines = [line for line in existing_lines if line.parent is not None]
        existing_top = {
            line.code: line
            for line in existing_lines if line.parent is None
        }

        new_top = {}
        modified = {}

        # For every line in new lines, update/create quantities on the lines.
        for code, line in new_invoice_lines.iteritems():
            ex = existing_top.get(code)

            # Are we deleting a line?
            if not line.quantity:
                if not ex:
                    # There's nothing to delete.
                    pass
                else:
                    line.quantity = 0  # We'll find these in a second to delete them.
            else:
                price = pricelist[code]  # this should be guaranteed because of the IL check above.
                # Does the line already exist?  If so, update the quantity and pricing.  We'll sync the subitems later.
                if ex:
                    ex.update(quantity=line.quantity, product=line.product, price=price, pricedate=self.pricetable_date)
                    modified[code] = ex
                else:
                    # otherwise make a brand new one.
                    ex = InvoiceLine()
                    ex.agreement = self
                    ex.update(quantity=line.quantity, product=line.product, price=price, pricedate=self.pricetable_date)
                    new_top[code] = ex

        # okay.  things deleted aren't being tracked through modified, and should just be deleted now (with their children, which are no longer useful)
        to_delete = [ex for ex in existing_top if ex.quantity == 0]
        for ex in to_delete:
            # find the child of the line I'm about to delete.
            children_to_delete = [c for c in child_lines if c.parent_id == ex.pk]
            # Delete them.
            for c in children_to_delete:
                child_lines.remove(c)
                c.delete()
            # delete the line.
            ex.delete()

        # Here are all the top lines we have.
        top_lines = {line.product_id: line for line in new_top.values() + modified.values()}

        lines_to_sync = top_lines.values()
        # child_lines is a list of lines that have parents.  As we resync the children of new_lines, we'll reuse anything in there that matches, and
        # append them to the end of lines_to_sync, so that THEY then get synced.
        # Then, we'll remove anything that's still left in child_lines.  #foolproof.

        def find_existing_child(parent, code):
            if not parent.pk:
                return None
            return first(child_lines, lambda line: line.parent_id == parent.pk and line.product_id == code)

        def sync_child_lines(line):
            prod = products.get(line.product_id)
            if not prod:
                return
            contents = {pc.code: pc for pc in prod.contents.all()}
            for code, pc in contents.iteritems():
                child = find_existing_child(parent=line, code=code)
                if child:
                    # This can't be reused again.
                    child_lines.remove(child)
                    child.quantity = pc.quantity * line.quantity
                else:
                    child = InvoiceLine(parent=line, agreement=self, product=code, quantity=pc.quantity * line.quantity)
                if pc.upfront_strike:
                    child.upfront_strike = pc.upfront_strike
                elif pc.monthly_strike:
                    child.monthly_strike = pc.monthly_strike

                # Queue up this line to be synced for ITS children just in case.
                lines_to_sync.append(child)

        # Recursively create/update child lines and put them in lines_to_sync.
        pos = 0
        while pos < len(lines_to_sync):
            line = lines_to_sync[pos]
            sync_child_lines(line)

        # Anything left in child_lines is junk now.
        for bad_child in child_lines:
            bad_child.delete()

        # Everything in lines_to_sync is real, and because of how the recursion worked,
        # saving them in order should satisfy the self-foreign key.  (Everything lower refers to nothing or
        # to a line higher in the list.)

        # Save all the invoice lines.
        for line in lines_to_sync:
            line.save()



    class Meta:
        verbose_name = u'Customer Agreement'
        verbose_name_plural = u'Customer Agreements'
        app_label = 'agreement'
