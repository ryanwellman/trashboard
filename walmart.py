#!/usr/bin/env python

from handy.connections import ChinaCursor, GladosCursor
from agreement.models import Agreement, Applicant, Address, Package, Campaign
from json import loads
from datetime import datetime


def Warehouse():
    cur = ChinaCursor()
    cur.SetCrossServerFlags()
    sql = '''
        SELECT Top 100 [agreement_id], [blob]
        FROM contract_details
    '''
    cur.execute(sql)
    merchandise = cur.fetch_all()

    for m in merchandise:
        blob = loads(m['blob'])

        agreement = Agreement()

        agreement.id = m['agreement_id']

        blob_campaign = blob['campaign_id'].upper()
        campaign = Campaign.objects.filter(name=blob_campaign)
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
            campaign_id = campaign[0].campaign_id
        agreement.campaign_id = campaign_id

        applicant_id = None
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
            phone = blob['phone1']
            applicant_id = Customer(fname, lname, initial, phone)
        agreement.applicant_id = applicant_id

        agreement.coapplicant = None

        billing_address_id = None
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
        agreement.billing_address_id = billing_address_id
        agreement.system_address_id = billing_address_id

        agreement.pricetable_date = datetime(blob['date_created']['year'],
                                             blob['date_created']['month'],
                                             blob['date_created']['day'],
                                             blob['date_created']['hour'],
                                             blob['date_created']['minute'])

        agreement.email = blob['email']

        approved = None
        if blob['credit_status'] == 'APPROVED DCS':
            approved = 'DCS'
        else:
            approved = blob['credit_status']
        agreement.approved = approved

        agreement.package_id = None
        if not blob['package']:
            agreement.package_id = ''
        else:
            selected_package = blob['package']['code'].lower()
            package = Package.objects.get(code=selected_package)
            agreement.package_id = package.pk

        agreement.shipping = None
        if not blob['shipping']:
            agreement.shipping = ''
        else:
            agreement.shipping = blob['shipping']['code']

        agreement.monitoring = None
        if not blob['monitoring']:
            agreement.monitoring = 'None Given'
        else:
            agreement.monitoring = blob['monitoring']['code']

        agreement.floorplan = blob['floorplan']
        agreement.promo_code = 'None Given'
        agreement.done_premium = '1'
        agreement.done_combo = '1'
        agreement.done_alacarte = '1'
        agreement.done_closing = '1'
        agreement.done_package = '1'
        agreement.done_promos = '1'

        agreement.save()

    return merchandise

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
