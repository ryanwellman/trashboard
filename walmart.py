#!/usr/bin/env python

from handy.connections import ChinaCursor, GladosCursor
from handy.jsonstuff import loads
from agreement.models import Agreement, Applicant, Address, Package, Campaign, InvoiceLine
from datetime import datetime


def Warehouse():
    china_cur = ChinaCursor()
    china_cur.SetCrossServerFlags()
    sql = '''
        SELECT cd.agreement_id, blob, date_created, date_modified as date_modified
        FROM contract_details cd
        LEFT JOIN contracts c on c.agreement_id = cd.agreement_id
    '''
    china_cur.execute(sql)
    campaigns = {c.pk: c for c in Campaign.objects.all()}
    existing = list(Agreement.objects.all().values_list('id', flat=True))

    while True:
        print "grabbing lines"
        merchandise = china_cur.fetch_many()

        for m in merchandise:
            if m['agreement_id'] in existing:
                continue
            blob = loads(m['blob'])
            blob['date_created'] = m['date_created']
            blob['date_modified'] = m['date_modified']

            agreement = Agreement()

            agreement.id = m['agreement_id']
            print "id", agreement.id

            blob_campaign = blob['campaign_id'].upper()
            campaign = campaigns.get(blob_campaign)

            campaign_id = None
            if not campaign:
                cur = GladosCursor()
                sql = '''
                    SELECT campaign_id, name
                    FROM campaigns
                    WHERE campaign_id = ?
                '''
                cur.execute(sql, [blob_campaign])
                prev_campaign = cur.fetchone()

                if not prev_campaign:
                    new_campaign = Campaign()
                    new_campaign.campaign_id = blob_campaign
                    new_campaign.name = blob_campaign
                    new_campaign.save()
                    campaign_id = new_campaign.pk
                else:
                    new_campaign = Campaign()
                    new_campaign.campaign_id = blob_campaign
                    new_campaign.name = prev_campaign.name
                    new_campaign.save()
                    campaign_id = new_campaign.pk
            else:
                campaign_id = campaign.campaign_id
            agreement.campaign_id = campaign_id

            applicant_id = None
            if 'applicant' in blob.keys():
                if not blob['applicant']:
                    fname = ''
                    lname = ''
                    initial = ''
                    phone = ''
                    applicant_id = Customer(fname, lname, initial, phone)
                else:
                    fname = blob['applicant']['first_name']
                    lname = blob['applicant']['last_name']
                    initial = blob['applicant']['middle_initial']
                    phone = None
                    if not blob['phone1']:
                        phone = ''
                    else:
                        phone = blob['phone1']
                    applicant_id = Customer(fname, lname, initial, phone)
            else:
                fname = ''
                lname = ''
                initial = ''
                phone = ''
                applicant_id = Customer(fname, lname, initial, phone)
            agreement.applicant_id = applicant_id

            agreement.coapplicant = None
            if 'coapplicant' in blob.keys():
                if not blob['coapplicant']:
                    agreement.coapplicant_id = None
                else:
                    fname = blob['coapplicant']['first_name']
                    lname = blob['coapplicant']['last_name']
                    initial = blob['coapplicant']['middle_initial']
                    phone = blob['phone1']
                    create_coapplicant = Customer(fname, lname, initial, phone)
                    agreement.coapplicant_id = create_coapplicant

            billing_address_id = None
            if 'address' in blob.keys():
                if not blob['address']:
                    address = ''
                    city = ''
                    state = ''
                    zipcode = ''
                    country = ''
                    billing_address_id = Location(address, city, state, zipcode, country)
                else:
                    address = blob['address']['address1']
                    city = blob['address']['city']
                    state = blob['address']['state']
                    zipcode = blob['address']['zipcode']
                    country = 'US'
                    billing_address_id = Location(address, city, state, zipcode, country)
            else:
                address = ''
                city = ''
                state = ''
                zipcode = ''
                country = ''
                billing_address_id = Location(address, city, state, zipcode, country)
            agreement.billing_address_id = billing_address_id
            agreement.system_address_id = billing_address_id

            # going to use this date again, so just going to create it first before assignment
            pricetable_date = blob['date_created']
            agreement.pricetable_date = pricetable_date or datetime(1900, 1, 1, 0, 0)

            agreement.email = blob['email']

            approved = None
            if blob['credit_status'] == 'APPROVED DCS':
                approved = 'DCS'
            else:
                approved = blob['credit_status']
            agreement.approved = approved

            agreement.package_id = None
            if 'package' in blob.keys():
                if not blob['package']:
                    agreement.package_id = ''
                else:
                    selected_package = blob['package']['code'].lower()
                    package = Package.objects.get(code=selected_package)
                    agreement.package_id = package.pk

            agreement.shipping = None
            if 'shipping' in blob.keys():
                if not blob['shipping']:
                    agreement.shipping = ''
                else:
                    agreement.shipping = blob['shipping']['code']
            else:
                agreement.shipping = ''

            agreement.monitoring = None
            if 'monitoring' in blob.keys():
                if not blob['monitoring']:
                    agreement.monitoring = ''
                else:
                    agreement.monitoring = blob['monitoring']['code']
            else:
                agreement.monitoring = ''

            agreement.floorplan = blob['floorplan']
            agreement.promo_code = 'None Given'

            # since these are existing records, we will assume that these things have been done
            agreement.done_premium = '1'
            agreement.done_combo = '1'
            agreement.done_alacarte = '1'
            agreement.done_closing = '1'
            agreement.done_package = '1'
            agreement.done_promos = '1'

            agreement.save()

            agreement_object = Agreement.objects.get(id=m['agreement_id'])

            if 'package' in blob.keys():
                package = blob['package']
                if package:
                    invoice = InvoiceLine()
                    invoice.agreement = agreement_object
                    invoice.note = ''
                    invoice.product = package['code']
                    invoice.pricetable = blob['pricetable']
                    invoice.quantity = '1'
                    invoice.upfront_each = package['upfront_price']
                    invoice.upfront_total = package['upfront_price']
                    invoice.upfront_strike = package['retail_price']
                    invoice.monthly_each = package['monthly_price']
                    invoice.monthly_total = package['monthly_price']
                    invoice.save()

            if 'monitoring' in blob.keys():
                monitoring = blob['monitoring']
                if monitoring:
                    invoice = InvoiceLine()
                    invoice.agreement = agreement_object
                    invoice.note = ''
                    invoice.product = monitoring['code']
                    invoice.pricetable = blob['pricetable']
                    invoice.quantity = '1'
                    invoice.pricedate = pricetable_date
                    invoice.upfront_each = monitoring['upfront_price']
                    invoice.upfront_total = monitoring['upfront_price']
                    invoice.upfront_strike = monitoring['retail_price']
                    invoice.monthly_each = monitoring['monthly_price']
                    invoice.monthly_total = monitoring['monthly_price']
                    invoice.save()

            equipment = blob['equipment']
            if equipment:
                for e in equipment:
                    invoice = InvoiceLine()
                    invoice.agreement = agreement_object
                    # there is a reason in the blob, perhaps note needs to be changed to reason?
                    invoice.note = e['reason']
                    invoice.product = e['part']
                    invoice.pricetable = blob['pricetable']
                    invoice.quantity = e['quantity']
                    invoice.pricedate = pricetable_date
                    invoice.upfront_each = None
                    if e['upfront_price'] == 0:
                        invoice.upfront_each = e['upfront_price']
                    else:
                        invoice.upfront_each = e['upfront_price']
                    invoice.upfront_total = float(invoice.upfront_each) * invoice.quantity
                    invoice.monthly_each = None
                    if e['monthly_price'] == 0:
                        invoice.monthly_each = e['monthly_price']
                    else:
                        invoice.monthly_each = e['monthly_price']
                    invoice.monthly_total = float(invoice.monthly_each) * invoice.quantity
                    invoice.save()

            if 'shipping' in blob.keys():
                shipping = blob['shipping']
                if shipping:
                    invoice = InvoiceLine()
                    invoice.agreement = agreement_object
                    invoice.note = ''
                    invoice.product = shipping['code']
                    invoice.pricetable = blob['pricetable']
                    invoice.quantity = '1'
                    invoice.pricedate = pricetable_date
                    invoice.upfront_each = shipping['upfront_price']
                    invoice.upfront_total = shipping['upfront_price']
                    invoice.save()

            services = blob['services']
            if services:
                for s in services:
                    invoice = InvoiceLine()
                    invoice.agreement = agreement_object
                    invoice.note = ''
                    invoice.product = s['service']
                    invoice.pricetable = blob['pricetable']
                    invoice.quantity = '1'
                    invoice.pricedate = pricetable_date
                    invoice.upfront_price = s['upfront_price']
                    invoice.upfront_total = s['upfront_price']
                    invoice.upfront_strike = s['retail_price']
                    invoice.monthly_price = s['monthly_price']
                    invoice.monthly_total = s['monthly_price']
                    invoice.save()

    return

def Customer(fname, lname, initial, phone):
    applicant = Applicant()
    applicant.fname = fname
    applicant.lname = lname
    applicant.initial = initial
    applicant.phone = phone
    applicant.save()

    return applicant.id


def Location(address, city, state, zipcode, country):
    cust_address = Address()
    cust_address.address = address
    cust_address.city = city
    cust_address.state = state
    cust_address.zip = zipcode
    cust_address.county = country
    cust_address.save()

    return cust_address.id

if __name__ == '__main__':
    Warehouse()

