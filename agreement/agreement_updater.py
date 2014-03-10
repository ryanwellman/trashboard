from datetime import datetime
from django.utils import timezone

from handy import intor, first
from collections import defaultdict
from handy.controller import JsonResponse
from agreement.models import Applicant, Address, Campaign, Package, Product, Agreement, InvoiceLine, ProductContent
#from handy.reflector import TypesFromAgreement

class IL(object):
    def __init__(self, line, updater):
        self.updater = updater
        print "In IL init, line is %r" % (line,)
        self.code = line.get('code')
        self.quantity = intor(line.get('quantity'))
        self.traded = line.get('traded', False)

        self.product = updater.products.get(self.code)
        self.price = updater.prices.get(self.code)
        self.parent = None  # incoming lines from json never have a parent.

        if not self.code or self.quantity is None:
            errors.append('Invalid invoiceline update: %r' % (line,))
        elif not self.product:
            errors.append('The product %s could not be found.' % line.code)
        elif not self.price:
            errors.append('The product %s is not available for the campaign %s' % self.campaign_id)





class AgreementUpdater(object):
    def __init__(self, agreement, blob):
        self.agreement = agreement
        self.errors = []
        self.messages = []
        self.blob = blob

        self.products = Product.get_all_products()
        self.prices = agreement.campaign.get_product_prices()

        pcs = ProductContent.objects.all()
        self.product_contents = defaultdict(list)
        for pc in pcs:
            self.product_contents[pc.included_in_id].append(pc)

        self.final_children = []


    def update_from_blob(self, update_blob):
        # this is where the vast majority of the magic is going to happen.

        if 'applicant' in update_blob:
            # We are assigning applicant.  If we don't have one already, make it.
            target_applicant = self.agreement.applicant
            if not target_applicant:
                target_applicant = Applicant()

            target_applicant.update_from_blob(update_blob['applicant'], self)

            target_applicant.save()
            self.agreement.applicant = target_applicant # Put it back on myself

        if 'coapplicant' in update_blob:
            # We are assigning applicant.  If we don't have one already, make it.
            target_applicant = self.agreement.coapplicant
            if not target_applicant:
                target_applicant = Applicant()

            target_applicant.update_from_blob(update_blob['coapplicant'], self)
            target_applicant.save()

            self.agreement.coapplicant = target_applicant # Put it back on myself

        if 'system_address' in update_blob:
            target_address = self.agreement.system_address
            if not target_address:
                target_address = Address()

            target_address.update_from_blob(update_blob['system_address'], self)
            target_address.save()
            self.agreement.system_address = target_address

        if 'invoice_lines' in update_blob:
            self.update_invoice_lines()

        #return errors


    def update_invoice_lines(self):

        # The incoming invoice lines should look like:
        '''
        [{
            'code': 'COPPER',
            'quantity': 1
            'traded': true // or not present.
        }, ...]
        '''

        # coerce the incoming invoice lines:
        incoming_lines = [IL(line, updater=self) for line in self.blob['invoice_lines']]
        # If the IL constructor put any errors in, stop now.
        if self.errors:
            return

        # Next get every existing invoice line.
        self.existing_lines = list(self.agreement.invoice_lines.all())
        self.unclaimed_lines = list(self.existing_lines)  # Unclaim all existing lines.  We may reclaim them soon.

        # this is the list of lines that will be on the agreement at the end:
        self.final_lines = []

        # First, do every line that came in from the system NOT traded.
        # Invoice Lines for these should all be TOP.
        # (This includes package, monitoring, alacarte, but not children, mandatory services...)
        for il in incoming_lines:
            if il.traded:
                continue
            # il is a fakey line.
            line = self.reclaim_line(code=il.code, line_type='TOP')
            if not line:
                line = InvoiceLine(agreement=self.agreement)
            line.update_top(product=il.product, quantity=il.quantity, price=il.price, pricedate=self.agreement.pricetable_date)

            self.final_lines.append(line)

        # Now do it again for trade lines.
        for il in incoming_lines:
            if not il.traded:
                continue

            line = self.reclaim_line(code=il.code, line_type='TRADE')
            if not line:
                line = InvoiceLine(agreement=self.agreement)

            line.update_trade(product=il.product, quantity=il.quantity, price=il.price, pricedate=self.agreement.pricetable_date)

            self.final_lines.append(line)

        # Save any lines in final_lines because they'll need pks for their children.
        for line in self.final_lines:
            line.save()

        print "Final lines BEFORE CHILD SYNC:"
        for line in self.final_lines:
            print "{}, {}, {}".format(line.code, line.quantity, line.traded)


        # loop through, adding mandatory items and syncing children until no changes are made.
        loops = 0
        self.sync_all_children()
        while True:
            # Next, we need to process mandatory items.
            changed = self.add_mandatory_items()

            # Then, sync children again.
            changed = self.sync_all_children() or changed

            if not changed:
                break

            loops += 1
            if loops >= 10:
                self.errors.append("Probably an infinite loop in mandatories/children.  Needs fixin.")
                break

        # Next reclaim/create a permit line if needed.
        self.add_permit_lines()

        self.sanity_check()

        print "Final lines:"
        for line in self.final_lines:
            print "{}, {}, {}".format(line.code, line.quantity, line.traded)

        # Finally, any lines that are in existing_lines but not in final_lines should be deleted.
        for orphan in self.existing_lines:
            if orphan in self.final_lines:
                continue
            orphan.delete()

    def sanity_check(self):
        # don't even know what to do here.
        return


    def reclaim_line(self, code, parent_id=None, line_type=None, note=None):
        for line in list(self.unclaimed_lines):
            if line.code != code:
                continue

            if parent_id is not None and parent_id != line.parent_id:
                continue

            if line_type is not None and line_type != line.line_type:
                continue

            if note is not None and note != line.note:
                continue



            # If we're not looking for a traded/mandatory line, then it's either a top or a child line.
            #if not traded and not mandatory:
            #    # so its parent needs to be whatever we're looking for
            #    if line.parent_id != parent_id:
            #        continue

            # If we get here, we're reclaiming it.
            self.unclaimed_lines.remove(line)
            return line

        # I couldn't find a line to reclaim.
        return None


    def by_code(self, ilines):
        return {line.code: line for line in ilines}

    '''
    def sync_top_lines(self, existing, incoming, traded):
        final = []  # Put the lines we used into here.  Anything not in here will be deleted eventually.

        # For every line in new lines, update/create quantities on the lines.
        for code, inc in incoming.iteritems():
            if line.quantity:
                ex = existing.get(code)
                # Does the line already exist?  If so, update the quantity and pricing.  We'll sync the subitems later.
                if ex:
                    ex.update(quantity=line.quantity, product=line.product, price=price, pricedate=self.pricetable_date, traded=traded)
                    final.append(ex) # Good job!
                else:
                    # otherwise make a brand new one.
                    new = InvoiceLine()
                    new.agreement = self.agreement
                    new.update(quantity=line.quantity, product=line.product, price=price, pricedate=self.pricetable_date, traded=traded)
                    final.append(new)

        return final
    '''

    def sync_all_children(self):
        # First, unclaim any child lines we've claimed in a previous call to this function.  They'll get reclaimed in this function if necessary.
        self.unclaimed_lines = list(set(self.unclaimed_lines + [line for line in self.final_lines if not line.traded and line.parent]))

        # This is a copy of self.final_lines, filtered down to not include child lines (except trades)
        # It's used to detect differences at the end from self.final_lines, and will get assigned there at the end.
        final_lines = [line for line in self.final_lines if line.traded or not line.parent]

        # This function can be called more than once in a row, which is necessary if more lines get added as a result
        # of child lines being added.  (You add a smoke package, it has a smoke detector, which requires the smoke service,
        # hypothetically has a smoke permit kit or something.)

        # A queue of lines that need their children synced.  Starts with final_lines which is the top and traded lines.
        lines_to_sync = list(final_lines)


        pos = 0
        while pos < len(lines_to_sync):
            # walk through each line and sync its children.  As children get added, they'll be queued onto
            # the end of this loop, so they can get their nested children.
            line = lines_to_sync[pos]
            pos += 1

            prod = self.products.get(line.code)
            if not prod:
                self.errors.append("Could not find product %r to sync child lines on line %r" % (line.code, line.pk))
                continue
            # Index the contents of this line's product.
            contents = self.by_code(self.product_contents.get(prod.code, []))

            # for every product in that product:
            for code, pc in contents.iteritems():
                child = self.reclaim_line(parent_id=line.pk, code=code, line_type='CHILD')
                if not child:
                    # If I wasn't able to reclaim an existing child, we need to make a new one for this agreement/line:
                    child = InvoiceLine(agreement=self.agreement, parent=line)

                # sync the child line with the product (gets updated quantity, product type, category, etc.)
                child.update_child(product=self.products[code], pc=pc, parent_line=line)

                # Save this child. It's either been updated or is new.
                child.save()

                # Queue up this line to be synced for ITS children
                lines_to_sync.append(child)
                # and add it to final_lines
                final_lines.append(child)

        # Did the final set of lines change from what we had before?
        changed = set(final_lines) ^ set(self.final_lines)

        # And then, assign the final set of children.
        self.final_lines = final_lines

        return bool(changed)

    def add_mandatory_items(self):

        self.total_quantities = defaultdict(lambda: 0)
        for line in self.final_lines:
            self.total_quantities[line.code] += line.quantity

        changed = False
        #mandatory_adders = Reflector.TypesFromAgreement(mandatories, MandatoryRequirement)
        #mandatory_adders = []
        from mandatory_requirements import MandatoryRequirements

        for reqname, mr_kls in MandatoryRequirements.iteritems():
            print "About to check reqname=%r, mr_kls=%r" % (reqname, mr_kls)
            mr = mr_kls(updater=self)
            changed = mr.check() or changed

        return changed

    def add_mandatory_product(self, code, quantity):
        # The function needs to check to see if it is already satisfied before
        # calling this. This function will always reclaim or create a new line
        # with the specified quantity. this is because add_mandatory_items
        # gets called multiple times, but does NOT unclaim everything like
        # sync_all_children does, because it may be that the mandatory items
        # themselves require more mandatory items. (Ex: for some reason,
        # businesses in california MUST have a smoke detector.)


        mp = self.reclaim_line(code=code, line_type='MANDATORY')
        if not mp:
            mp = InvoiceLine(agreement=self.agreement)
            product = self.products.get(code)
            if not product:
                self.errors.append('Could not add mandatory product %r' % code)
                return
            price = self.prices.get(code)
            if not price:
                self.errors.append('Mandatory product %r has no price.  Campaign=%r' % (code, self.agreement.campaign_id))

            mp.update_mandatory(quantity=quantity, product=product, price=price, pricedate=self.agreement.pricetable_date)

        mp.quantity = quantity
        mp.save()
        self.final_lines.append(mp)

    def add_permit_lines(self):
        from regional.restrictions import GetMatchingPRsByZip

        if not self.agreement.system_address.zip:
            return

        property_type = 'commercial' if self.agreement.floorplan == 'Business' else 'residential'

        prs = GetMatchingPRsByZip(self.agreement.system_address.zip, property_type, asof=datetime.now())
        print "PRs found: %r" % prs
        permits = [pr for pr in prs if pr.permit_fee or pr.addendum_fee]

        # These are the lines we need permits for.  We're going to cheat
        # our faces off and use the note column for this.

        for pr in permits:
            # reclaim or create a permit line.
            pnote = ';'.join([pr.override_type or pr.region_type, ', '.join(pr.override_name or pr.region_name)])
            pline = self.reclaim_line(code='PERMIT', line_type='PERMIT', note=pnote)
            if not pline:
                pline = InvoiceLine(agreement=self.agreement, line_type='PERMIT')

            pline.update_permit(pr, permit_product=self.products['PERMIT'])
            pline.save()

            # Put the permit line onto the final part.
            self.final_lines.append(pline)

    def json_response(self):
        prod_dict = {code: prod.as_jsonable() for code, prod in self.products.iteritems()}
        for code, prod_json in prod_dict.iteritems():
            for pc in self.product_contents.get(code, []):
                prod_json['contents'].append(pc.as_jsonable())

        return JsonResponse(content={
            'agreement': self.agreement.as_jsonable(),
            'errors': self.errors,
            'messages': self.messages,
            'catalog': {
                'products': {code: prod.as_jsonable() for code, prod in self.products.iteritems()},
                'prices': {code: price.as_jsonable() for code, price in self.prices.iteritems()}
            }
        })


