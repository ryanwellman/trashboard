#!/usr/bin/env python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from org.models import *
from inventory.models import *

from handy.connections import DashboardCursor
cur = DashboardCursor()

camps = cur.fetch_all('''
    select oo.code as org_code, oo.distribution_addr as distribution_email,
    oo.name as org_name,
    c.campaign_id, c.name as campaign_name, c.is_enabled as campaign_enabled, c.pricetable_id, pt.name as pricetable_name
    from org_organization oo
    inner join org_organization_campaigns ooc on oo.id = ooc.organization_id
    inner join campaigns_campaign c on ooc.campaign_id = c.campaign_id
    inner join inventory_pricetable pt on c.pricetable_id = pt.id
    ''')

from pprint import pprint

pprint(camps)
inside_pt = PriceTable.objects.get(pk='inside:2014-03-18')
csp_pt = PriceTable.objects.get(pk='csp:2014-03-18')



inside_group = PriceGroup(name='inside')
inside_group.save()
PGMembership(pricegroup=inside_group, pricetable=inside_pt).save()

#inside_group.pricetables.add(inside_pt)

csp_group = PriceGroup(name='csp')
csp_group.save()
#csp_group.pricetables.add(csp_pt)
PGMembership(pricegroup=csp_group, pricetable=csp_pt).save()

organizations = {}


 # {'code': 'vue',
 #  'distribution_addr': 'vuesecurity@live.com',
 #  'id': 391L,
 #  'name': 'Vue Security Inc.',
 #  'short_code': 'vue'}

for camp in camps:
    org_code = camp['org_code']
    if org_code not in organizations:
        o = Organization(org_code=org_code, name=camp['org_name'], distribution_email=camp['distribution_email'])
        if org_code == 'protectamerica':
            o.pricegroup = inside_group
        else:
            o.pricegroup = csp_group
        o.save()
        organizations[org_code] = o
    else:
        o = organizations[org_code]

    c = Campaign(
            campaign_id=camp['campaign_id'],
            organization=o,
            name=camp['campaign_name']
        )
    c.save()

# that should have brought everyone.