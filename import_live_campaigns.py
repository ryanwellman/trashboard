#!/usr/bin/env python
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from org.models import *
from inventory.models import *
from handy.connections import DashboardCursor
from django.contrib.contenttypes.models import ContentType

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

perms = {}
agreement_ct = ContentType.objects.get(app_label='agreement', model='Agreement')
perm_map = {
# Org Permissions:
'create_draft' : 'Can Create Drafts',
'view_others_drafts': 'Can View Drafts Owned by Other Agents',
'work_others_drafts': 'Can Work Drafts Owned by Other Agents',
'takeover_others_drafts': 'Can Take Over Drafts Owned by Other Agents',
'rewalk_contract': 'Can Rewalk Drafts In Same Organization',


# Permissions:
'approve_exception': 'Can Approve Exceptions',
'override credit': 'Can Override Credit Response',
'bypass_upfront_authorization': 'Can Bypass Upfront Authorization',
'view_worksheet': 'Can View Worksheets'}

for perm, name in perm_map.items():
    perms[perm] = gooN(Permission, codename=perm, content_type=agreement_ct)
    if not perms[perm]:
        perms[perm] = Permission(codename=perm, content_type=agreement_ct)
    perms[perm].name = name
    perms[perm].save()

role_map = {
    'agent_1': [
        'create_draft',
    ],
    'agent_2': [
        'create_draft', 'view_others_drafts',
    ],
    'agent_3': [
        'create_draft', 'view_others_drafts', 'work_others_drafts',
    ],
    'agent_4': [
        'create_draft', 'view_others_drafts', 'work_others_drafts', 'takeover_others_drafts'
    ],
    'inside_sales': [
        'view_others_drafts', 'work_others_drafts', 'takeover_others_drafts', 'rewalk_contract',
    ],
}






''' RESEARCH


select oo.code as org_code, oo.distribution_addr as distribution_email,
oo.name as org_name,
c.campaign_id, c.name as campaign_name, c.is_enabled as campaign_enabled, c.pricetable_id, pt.name as pricetable_name
from org_organization oo
inner join org_organization_campaigns ooc on oo.id = ooc.organization_id
inner join campaigns_campaign c on ooc.campaign_id = c.campaign_id
inner join inventory_pricetable pt on c.pricetable_id = pt.id


select ou.id, ou.organization_id, username,
max(case when manager_role.id is not null then 1 else 0 end) as is_manager,
max(case when p.id is not null then 1 else 0 end) as users_can_view_others
from org_orguser ou
left join org_orguser_roles oor on ou.id = oor.orguser_id
left join org_role manager_role on oor.role_id = manager_role.id and manager_role.name = 'Managers'
left join org_role user_role on oor.role_id = user_role.id and user_role.name = 'Users'
left join org_role_permissions orp on orp.role_id = user_role.id
left join auth_permission p on p.id = orp.permission_id and p.codename = 'view_others'
group by ou.id
;

'''
