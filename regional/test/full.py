import re
import string
from os import path
from glob import glob
from decimal import Decimal

from django.test import TestCase

from ..restrictions import (can_sell_fire_detectors,
                            get_install_method_permissions,
                            get_permit, get_addendum)
from ..models import Region

class Tests(TestCase):
    fixtures = ['us_zipcode_entries.json']

    def test_all(self): # one test so it doesn't take so freaking long

        def fire_detectors(self):
            property_types = (
                'RENTER',
                'HOMEOWNER',
                'COMMERCIAL',
            )

            for zipcode in xrange(0, 99999):
                zipcode = '%05d' % zipcode
                res = can_sell_fire_detectors(zipcode, 'COMMERCIAL')[0]
                self.assertFalse(res, msg=zipcode)

            no_install_zips = (
                '19707', #DE
                '83311', #ID
                '67512', #KS
                '71302', #LA
                '01199', #MA
                '49010', #MI
                '59312', #MT
                '68303', #NE
                '89821', #NV
                '58710', #ND
                '44310', #OH
                '02836', #RI
                '57349', #SD
                '05257', #VT
                '82832', #WY
                '33061', #Pompano Beach, FL
                '81620', #Eagle County, CO
            )
            for zipcode in no_install_zips:
                for property_type in property_types:
                    msg = '%s %s' % (zipcode, property_type)
                    res = can_sell_fire_detectors(zipcode, property_type)[0]
                    self.assertFalse(res, msg=msg)

            no_self_install_zips = (
                '35801', #Huntsville, AL
                '74012', #Broken Arrow, OK
            )
            for zipcode in no_self_install_zips:
                for property_type in property_types:
                    msg = '%s %s' % (zipcode, property_type)
                    res = can_sell_fire_detectors(zipcode, property_type)[0]
                    self.assertFalse(res, msg=msg)

            no_tech_install_zips = (
                '98855', #WA
                '54805', #WI
            )
            for zipcode in no_tech_install_zips:
                for property_type in property_types:
                    msg = '%s %s' % (zipcode, property_type)
                    res = can_sell_fire_detectors(zipcode, property_type, True)[0]
                    self.assertFalse(res, msg=msg)

            zipcode = '04862' # ME
            self.assertFalse(can_sell_fire_detectors(zipcode, 'RENTER')[0])
            self.assertTrue(can_sell_fire_detectors(zipcode, 'HOMEOWNER')[0])

            install_zips = (
                '35950', #AL
                '99503', #AK
                '86506', #AZ
                '72002', #AR
                '95476', #CA
                '81154', #CO
                '06002', #CT
                '32420', #FL
                '31703', #GA
                '96708', #HI
                '62441', #IL
                '47331', #IN
                '51354', #IA
                '42020', #KY
                '21230', #MD
                '56434', #MN
                '38603', #MS
                '63001', #MO
                '03220', #NH
                '08260', #NJ
                '87109', #NM
                '12204', #NY
                '27910', #NC
                '73401', #OK
                '97711', #OR
                '18210', #PA
                '29626', #SC
                '37745', #TN
                '79699', #TX
                '84754', #UT
                '22306', #VA
                '98003', #WA
                '20049', #DC
                '25003', #WV
                '54912', #WI
            )
            for zipcode in install_zips:
                self.assertTrue(can_sell_fire_detectors(zipcode, 'RENTER')[0],
                                msg=zipcode)
                self.assertTrue(can_sell_fire_detectors(zipcode, 'HOMEOWNER')[0],
                               msg=zipcode)


        def install_method(self):
            property_types = (
                'RENTER',
                'HOMEOWNER',
                'COMMERCIAL',
            )

            no_install_zips = (
                '00601', #PR
                '92334', #Fontana, CA
                '94537', #Fremont, CA
                '95381', #Turlock, CA
                '33060', #Pompano Beach, FL
                '60002', #Antioch, IL
                '62301', #Quincy, IL
                '63101', #St Louis, MO
                '97402', #Eugene, OR
                '57101', #Sioux Falls, SD
                '98146', #Burien, WA
                '98102', #Seattle, WA
                '98401', #Tacoma, WA
                '53202', #Milwaukee, WI
                '67203', #Sedgewick County, KS
                '40504', #Fayette County, KY
            )
            for zipcode in no_install_zips:
                for property_type in property_types:
                    msg = "%s %s" % (zipcode, property_type)
                    permissions = get_install_method_permissions(zipcode,
                                                                 property_type)
                    self.assertFalse(permissions['self_install'], msg=msg)
                    self.assertFalse(permissions['tech_install'], msg=msg)

            no_self_install_zips = (
                '35801', #Huntsville, AL
                '74011', #Broken Arrow, OK
                '35741',
                '35749',
                '35756',
                '35757',
                '35758',
                '35759',
                '35763',
                '35671',
                '35773',
            )
            for zipcode in no_self_install_zips:
                for property_type in property_types:
                    msg = "%s %s" % (zipcode, property_type)
                    permissions = get_install_method_permissions(zipcode,
                                                                 property_type)
                    self.assertFalse(permissions['self_install'], msg=msg)
                    self.assertTrue(permissions['tech_install'], msg=msg)

            no_tech_install_zips = (
                '99503', #AK
                '20049', #DC
                '96708', #HI
                '01199', #MA
                '04862', #ME
                '56434', #MN
                '59312', #MT
                '89821', #NV
                '12204', #NY
                '97711', #OR
                '02836', #RI
                '82832', #WY
                '36611', #Chickasaw, AL
                '62203', #East Saint Louis, IL
                '98014', #Carnation, WA
                '20611', #Charles County, MD
            )
            for zipcode in no_tech_install_zips:
                for property_type in property_types:
                    msg = "%s %s" % (zipcode, property_type)
                    permissions = get_install_method_permissions(zipcode,
                                                                 property_type)
                    self.assertTrue(permissions['self_install'], msg=msg)
                    self.assertFalse(permissions['tech_install'], msg=msg)

            permissions = get_install_method_permissions('83311', 'HOMEOWNER')
            self.assertTrue(permissions['self_install'])
            self.assertTrue(permissions['tech_install'])
            permissions = get_install_method_permissions('83311', 'RENTER')
            self.assertFalse(permissions['self_install'])
            self.assertFalse(permissions['tech_install'])
            permissions = get_install_method_permissions('83311', 'COMMERCIAL')
            self.assertFalse(permissions['self_install'])
            self.assertFalse(permissions['tech_install'])

            install_zips = (
                '35950', #AL
                '86506', #AZ
                '72002', #AR
                '95476', #CA
                '81154', #CO
                '06002', #CT
                '19707', #DE
                '32420', #FL
                '31703', #GA
                '62441', #IL
                '47331', #IN
                '51354', #IA
                '67512', #KS
                '42020', #KY
                '71302', #LA
                '49010', #MI
                '21230', #MD
                '63001', #MO
                '38603', #MS
                '27910', #NC
                '58710', #ND
                '68303', #NE
                '03220', #NH
                '08260', #NJ
                '87109', #NM
                '44310', #OH
                '73401', #OK
                '18210', #PA
                '29626', #SC
                '57349', #SD
                '37745', #TN
                '79699', #TX
                '84754', #UT
                '22306', #VA
                '05257', #VT
                '98003', #WA
                '54912', #WI
                '25003', #WV
            )
            for zipcode in install_zips:
                for property_type in property_types:
                    msg = "%s %s" % (zipcode, property_type)
                    permissions = get_install_method_permissions(zipcode,
                                                                 property_type)
                    self.assertTrue(permissions['self_install'], msg=msg)
                    self.assertTrue(permissions['tech_install'], msg=msg)


        def permits(self):
            no_form = {
                '35801': {'residential': 10, 'commercial': 10},  #Huntsville, AL
                '33101': {'residential': 82.50, 'commercial': 82.50},  #Miami, FL
                '31401': {'residential': 12, 'commercial': 24},  #Savannah, GA
                '35741': {'residential': 10, 'commercial': 10},
                '35749': {'residential': 10, 'commercial': 10},
                '35756': {'residential': 10, 'commercial': 10},
                '35757': {'residential': 10, 'commercial': 10},
                '35758': {'residential': 10, 'commercial': 10},
                '35759': {'residential': 10, 'commercial': 10},
                '35763': {'residential': 10, 'commercial': 10},
                '35671': {'residential': 10, 'commercial': 10},
                '35773': {'residential': 10, 'commercial': 10},
            }
            for zipcode in no_form:
                for res_com in ('residential', 'commercial'):
                    msg = "%s %s" % (zipcode, res_com)

                    expected_permit = no_form[zipcode]
                    price = Decimal(str(expected_permit[res_com]))
                    returned_permit = get_permit(zipcode, res_com)

                    self.assertEquals(returned_permit['price'], price, msg=msg)
                    self.assertEquals(returned_permit['url'], None, msg=msg)

            requires_form = {
                '85001': {'residential': 17, 'commercial': 17, 'url': '/static/permits/AZ/city-phoenix-all.pdf'}, #Phoenix, AZ
                '85239': {'residential': 10, 'commercial': 10, 'url': '/static/permits/AZ/city-maricopa-all.pdf'}, #Maricopa, AZ
                '95610': {'residential': 50, 'commercial': 50, 'url': '/static/permits/CA/city-citrus-heights-all.pdf'}, #Citrus Heights, CA
                '95624': {'residential': 50, 'commercial': 50, 'url': '/static/permits/CA/city-elk-grove-all.pdf'}, #Elk Grove, CA
                '94945': {'residential': 28, 'commercial': 28, 'url': '/static/permits/CA/city-novato-all.pdf'}, #Novato, CA
                '94601': {'residential': 25, 'commercial': 35, 'url': '/static/permits/CA/city-oakland-all.pdf'}, #Oakland, CA
                '96001': {'residential': 0, 'commercial': 0, 'url': '/static/permits/CA/city-redding-all.pdf'}, #Redding, CA
                '95661': {'residential': 30, 'commercial': 30, 'url': '/static/permits/CA/city-roseville-all.pdf'}, #Roseville, CA
                '94203': {'residential': 40, 'commercial': 40, 'url': '/static/permits/CA/city-sacramento-all.pdf'}, #Sacramento, CA
                '92101': {'residential': 100.25, 'commercial': 173.25, 'url': '/static/permits/CA/city-san-diego-all.pdf'}, #San Diego, CA
                '95401': {'residential': 10, 'commercial': 15, 'url': '/static/permits/CA/city-santa-rosa-all.pdf'}, #Santa Rosa, CA
                '33904': {'residential': 25, 'commercial': 25, 'url': '/static/permits/FL/city-cape-coral-all.pdf'}, #Cape Coral, FL
                '32601': {'residential': 18.50, 'commercial': 18.50, 'url': '/static/permits/FL/city-gainesville-all.pdf'}, #Gainesville, FL
                '33060': {'residential': 55.90, 'commercial': 55.90, 'url': '/static/permits/FL/city-pompano-beach-all.pdf'}, #Pompano Beach, FL
                '31701': {'residential': 0, 'commercial': 0, 'url': '/static/permits/GA/city-albany-all.pdf'}, #Albany, GA
                '62002': {'residential': 25, 'commercial': 50, 'url': '/static/permits/IL/city-alton-all.pdf'}, #Alton, IL
                '62201': {'residential': 25, 'commercial': 50, 'url': '/static/permits/IL/city-east-saint-louis-all.pdf'}, #East Saint Louis, IL
                '50061': {'residential': 22, 'commercial': 34, 'url': '/static/permits/IA/city-west-des-moines-all.pdf'}, #West Des Moines, IA
                '70501': {'residential': 20, 'commercial': 20, 'url': '/static/permits/LA/city-lafayette-all.pdf'}, #Lafayette, LA
                '63101': {'residential': 65, 'commercial': 90, 'url': '/static/permits/MO/city-saint-louis-all.pdf'}, #Saint Louis, MO
                '14201': {'residential': 20, 'commercial': 20, 'separate_forms': True, 'url_residential': '/static/permits/NY/city-buffalo-residential.pdf', 'url_commercial': '/static/permits/NY/city-buffalo-commercial.pdf'},  #Buffalo, NY
                '18015': {'residential': 25, 'commercial': 25, 'url': '/static/permits/PA/city-bethlehem-all.pdf'}, #Bethlehem, PA
                '75201': {'residential': 50, 'commercial': 100, 'url': '/static/permits/TX/city-dallas-all.pdf'}, #Dallas, TX
                '24501': {'residential': 0, 'commercial': 0, 'url': '/static/permits/VA/city-lynchburg-all.pdf'}, #Lynchburg, VA
                '23432': {'residential': 0, 'commercial': 0, 'url': '/static/permits/VA/city-suffolk-all.pdf'}, #Suffolk, VA
                '98001': {'residential': 24, 'commercial': 24, 'url': '/static/permits/WA/city-auburn-all.pdf'}, #Auburn, WA
                '98027': {'residential': 24, 'commercial': 24, 'url': '/static/permits/WA/city-issaquah-all.pdf'}, #Issaquah, WA
                '98439': {'residential': 24, 'commercial': 24, 'url': '/static/permits/WA/city-lakewood-all.pdf'}, #Lakewood, WA
                '98503': {'residential': 25, 'commercial': 50, 'url': '/static/permits/WA/city-olympia-all.pdf'}, #Olympia, WA
                '95004': {'residential': 50, 'commercial': 50, 'url': '/static/permits/CA/county-monterey-all.pdf'}, #Monterey, CA
                '94101': {'residential': 45, 'commercial': 70, 'url': '/static/permits/CA/county-san-francisco-all.pdf'}, #San Francisco, CA
                '80206': {'residential': 25, 'commercial': 25, 'url': '/static/permits/CO/county-denver-all.pdf'},  #Denver, CO
                '80135': {'residential': 40, 'commercial': 40, 'url': '/static/permits/CO/county-douglas-all.pdf'}, #Douglas, CO
                '32616': {'residential': 15, 'commercial': 15, 'url': '/static/permits/FL/county-alachua-all.pdf'}, #Alachua, FL
                '33920': {'residential': 25, 'commercial': 25, 'url': '/static/permits/FL/county-lee-all.pdf'}, #Lee, FL
                '32948': {'residential': 30, 'commercial': 30, 'url': '/static/permits/FL/county-indian-river-all.pdf'}, #Indian River, FL
                '70470': {'residential': 0, 'commercial': 0, 'url': '/static/permits/LA/county-saint-tammany-all.pdf'}, #Saint Tammany, LA
                '20847': {'residential': 30, 'commercial': 30, 'url': '/static/permits/MD/county-montgomery-all.pdf'}, #Montgomery, MD
                '20607': {'residential': 0, 'commercial': 50, 'url': '/static/permits/MD/county-prince-georges-all.pdf'}, #Prince Georges, MD
                '21711': {'residential': 0, 'commercial': 0, 'url': '/static/permits/MD/county-washington-all.pdf'}, #Washington, MD
                '89507': {'residential': 24, 'commercial': 24, 'url': '/static/permits/NV/county-washoe-all.pdf'}, #Washoe, NV
                '13206': {'residential': 30, 'commercial': 30, 'url': '/static/permits/NY/county-onondaga-all.pdf'}, #Onondaga, NY
                '22032': {'residential': 25, 'commercial': 25, 'url': '/static/permits/VA/county-fairfax-all.pdf'}, #Fairfax, VA
                '20103': {'residential': 0, 'commercial': 0, 'separate_forms': True, 'url_residential': '/static/permits/VA/county-loudoun-residential.pdf', 'url_commercial': '/static/permits/VA/county-loudoun-commercial.pdf'} #Loudoun, VA
            }
            for zipcode in requires_form:
                for res_com in ('residential', 'commercial'):
                    msg = "%s %s" % (zipcode, res_com)

                    permit = requires_form[zipcode]
                    price = Decimal(str(permit[res_com]))
                    url = permit.get('url_%s' % res_com, permit.get('url'))
                    returned_permit = get_permit(zipcode, res_com)
                    self.assertEquals(returned_permit['price'], price, msg=msg)
                    self.assertTrue(returned_permit['url'].endswith(url),
                                    msg=msg)

            no_permit = (
                '35950', #AL
                '99503', #AK
                '86506', #AZ
                '72002', #AR
                '95476', #CA
                '81154', #CO
                '06002', #CT
                '32420', #FL
                '30605', #GA
                '96708', #HI
                '62441', #IL
                '47331', #IN
                '51354', #IA
                '42020', #KY
                '21230', #MD
                '56434', #MN
                '38603', #MS
                '63001', #MO
                '03220', #NH
                '08260', #NJ
                '87109', #NM
                '12204', #NY
                '27910', #NC
                '73401', #OK
                '97711', #OR
                '18210', #PA
                '29626', #SC
                '37745', #TN
                '79699', #TX
                '84754', #UT
                '22910', #VA
                '98205', #WA
                '20049', #DC
                '25003', #WV
                '54912', #WI
            )
            for zipcode in no_permit:
                for res_com in ('residential', 'commercial'):
                    self.assertTrue(get_permit(zipcode, res_com) == None)

            check_for_missing_permit_files(requires_form)
            check_for_extra_permit_files()


        def check_for_missing_permit_files(requires_form):
            missing_permits = set()
            for zipcode in requires_form:
                for res_com in ('residential', 'commercial'):
                    permit = requires_form[zipcode]
                    url = permit['url_%s' % res_com] if permit.get('separate_forms') else permit['url']
                    permit_path = path.join(path.dirname(path.dirname(__file__)), url[1:])
                    if not path.exists(permit_path):
                        missing_permits.add(permit_path)

            missing_permits = list(missing_permits)
            missing_permits.sort()
            with open(path.join(path.dirname(__file__), 'missing_permits.txt'), 'w') as out:
                for permit in missing_permits:
                    out.write('%s\n' % permit)


        def check_for_extra_permit_files():
            extra_permits = set()
            permits = glob('apps/regional/static/permits/*/*')
            for permit in permits:
                permit = re.sub('apps/regional/static/permits/', '', permit)
                state = permit[:2].upper()
                if re.match('city', permit[3:]):
                    city = re.sub('city-|-all|-residential|-commercial|.pdf', '', permit[3:])
                    city = string.capwords(re.sub('-', ' ', city))
                    zipcode = Region.objects.filter(city=city, state=state)[0].zipcode
                    permit = get_permit(zipcode, 'residential')
                    if not permit or not permit.get('url'):
                        extra_permits.add('%s, %s' % (city, state))
                elif re.match('county', permit[3:]):
                    county = re.sub('county-|-all|-residential|-commercial|.pdf', '', permit[3:])
                    county = string.capwords(re.sub('-', ' ', county))
                    zipcode = Region.objects.filter(county=county, state=state)[0].zipcode
                    permit = get_permit(zipcode, 'residential')
                    if not permit or not permit.get('url'):
                        extra_permits.add('%s, %s' % (county, state))
            extra_permits = list(extra_permits)
            extra_permits.sort()
            with open(path.join(path.dirname(__file__), 'extra_permits.txt'), 'w') as out:
                for permit in extra_permits:
                    out.write('%s\n' % permit)


        def addendums(self):
            addendum_required = {
                '95350': 5, #Modesto, CA
                '89012': 5, #Henderson, NV
                '89044': 5, #Las Vegas, NV
                '89030': 5, #North Las Vegas, NV
                '84107': 5, #Murray, UT
                '84101': 5, #Salt Lake City, UT
                '84115': 5, #South Salt Lake City, UT
                '84119': 5, #Taylorsville, UT
                '84120': 5, #West Valley City, UT
                '33401': 0, #Palm Beach, FL
                '98225': 5, #Bellingham, WA
                '98501': 0, #Olympia, WA
                '98901': 5, #Yakima, WA
            }
            for zipcode, price in addendum_required.iteritems():
                price = Decimal(str(price))
                self.assertEquals(get_addendum(zipcode)['price'], price,
                                  msg=zipcode)

            no_addendum = (
                '35950', #AL
                '99503', #AK
                '86506', #AZ
                '72002', #AR
                '95476', #CA
                '81154', #CO
                '06002', #CT
                '32420', #FL
                '31703', #GA
                '96708', #HI
                '62441', #IL
                '47331', #IN
                '51354', #IA
                '42020', #KY
                '21230', #MD
                '56434', #MN
                '38603', #MS
                '63001', #MO
                '03220', #NH
                '08260', #NJ
                '87109', #NM
                '12204', #NY
                '27910', #NC
                '73401', #OK
                '97711', #OR
                '18210', #PA
                '29626', #SC
                '37745', #TN
                '79699', #TX
                '84754', #UT
                '22306', #VA
                '98003', #WA
                '20049', #DC
                '25003', #WV
                '54912', #WI
            )
            for zipcode in no_addendum:
                self.assertTrue(get_addendum(zipcode) == None)

        fire_detectors(self)
        install_method(self)
        permits(self)
        addendums(self)
