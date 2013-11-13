from annoying.decorators import render_to, ajax_request
from dynamicresponse.response import *
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
import json
from json import dumps, loads
from random import choice
from agreement.models import Agreement

@csrf_exempt
def dyn_json(request, agreement_id=None):
    # XXX: this method and the next one are trash
    agreement = None
    if agreement_id:
        agreement = get_object_or_404(Agreement.objects.all(), pk=agreement_id)
    
    blob = {}
    if request.method == 'POST':
        # create a new agreement and use .save()
        for key in request.POST:
            blob = loads(key)

        # debug
        print blob

        agreement = Agreement.objects.create(   name=blob['name'],
                                                address=blob['address'],
                                                city=blob['city'],
                                                state=blob['state'],
                                                zip=blob['zip'],
                                                approved=blob['approved']   )
        agreement.save()

        print agreement

    return SerializeOrRedirect(reverse(draw_test), blob)


def serve_json(request):
    # XXX: this method and the one befoer are trash
    agreement = Agreement.objects.order_by('?')[0]
    #agreement = Agreement.objects.raw('SELECT * FROM agreement_agreement ORDER BY RANDOM() LIMIT 1')

    ctx =   {   'name': agreement.name,
                'address': agreement.address,
                'city': agreement.city,
                'state': agreement.state,
                'zip': agreement.zip,
                'approved': agreement.approved
            }

    return SerializeOrRedirect(reverse(draw_test), ctx)

    #approval_states = ['approved', 'no hit', 'dcs']
    #
    #ctx =   {   'name': "Joe Blow",
    #            'address': "3490 Jeffro Lane",
    #            'city': "Austin",
    #            'state': "Texas",
    #            'zip': "78728",
    #            'approved': choice(approval_states)
    #        }
    #
    #return SerializeOrRedirect(reverse(draw_test), ctx)


@render_to('templates/container.html')
def draw_container(request):
	# uses render_to to draw the template
	return dict()


@render_to('templates/package.html')
def Package(request):
    packages = [
                {'name':'Copper', 'price':'$19.99/mo', 'xt':'1', 'dw':'3', 'mot':'1'},
                {'name':'Bronze', 'price':'$35.99/mo', 'xt':'1', 'dw':'7', 'mot':'1'},
                {'name':'Silver', 'price':'$37.99/mo', 'xt':'1', 'dw':'10', 'mot':'1'},
                {'name':'Gold', 'price':'$39.99/mo', 'xt':'1', 'dw':'12', 'mot':'1'},
                {'name':'Platinum', 'price':'$42.99/mo', 'xt':'1', 'dw':'15', 'mot':'1'}
            ]
    monitoring = [{'type':'Landline', 'rate':'$27.99/mo'},
                  {'type':'Broadband', 'rate':'$45.99/mo'},
                  {'type':'Cellular', 'rate':'$49.99/mo'}]
    Copper = [{'part':'Simon XT Control', 'points':'25', 'qty':'1'},
              {'part':'Door/Window Sensors', 'points':'5', 'qty':'3'},
              {'part':'Motion Detector', 'points':'10', 'qty':'2'}]
    Bronze = [{'part':'Simon XT Control', 'points':'25', 'qty':'1'},
              {'part':'Door/Window Sensors', 'points':'5', 'qty':'7'},
              {'part':'Motion Detector', 'points':'10', 'qty':'2'}]
    Silver = [{'part':'Simon XT Control', 'points':'25', 'qty':'1'},
              {'part':'Door/Window Sensors', 'points':'5', 'qty':'10'},
              {'part':'Motion Detector', 'points':'10', 'qty':'2'}]
    Gold = [{'part':'Simon XT Control', 'points':'25', 'qty':'1'},
            {'part':'Door/Window Sensors', 'points':'5', 'qty':'12'},
            {'part':'Motion Detector', 'points':'10', 'qty':'2'}]
    Platinum = [{'part':'Simon XT Control', 'points':'25', 'qty':'1'},
                {'part':'Door/Window Sensors', 'points':'5', 'qty':'15'},
                {'part':'Motion Detector', 'points':'10', 'qty':'2'}]
    security_sensors = [{'part':'Glass Break Sensor', 'points':'10', 'qty':'0'},
               {'part':'Low Temperature Sensor', 'points':'10', 'qty':'0'},
               {'part':'Motion Detector', 'points':'10', 'qty':'0'},
               {'part':'Door/Window Sensor', 'points':'5', 'qty':'0'},
               {'part':'Flood Sensor', 'points':'12', 'qty':'0'},
               {'part':'Garage Door Sensor', 'points':'8', 'qty':'0'}]
    accessories = [{'part':'Keychain Remote Control', 'points':'5', 'qty':'0'},
                   {'part':'Medical Panic Bracelet', 'points':'10', 'qty':'0'},
                   {'part':'Medical Panic Pendant', 'points':'12', 'qty':'0'},
                   {'part':'Mini Pinpad', 'points':'5', 'qty':'0'},
                   {'part':'Solar Light', 'points':'3', 'qty':'0'},
                   {'part':'Talking Keypad', 'points':'13', 'qty':'0'},
                   {'part':'XT Talking Touchscreen', 'points':'13', 'qty':'0'}]
    fire_sensors = [{'part':'Smoke Detector', 'points':'15', 'qty':'0'},
                    {'part':'Carbon Monoxide Detector', 'points':'10', 'qty':'0'}]
    home_automation = [{'part':'X10 Siren', 'points':'10', 'qty':'0'},
                       {'part':'X10 Socket Rocket', 'points':'9', 'qty':'0'},
                       {'part':'X10 Appliance Module', 'points':'9', 'qty':'0'}]
    security_panels = [{'part':'Simon 3', 'points':'25', 'qty':'0'},
                       {'part':'Simon XT', 'points':'25', 'qty':'0'},
                       {'part':'Talkover Device', 'points':'10', 'qty':'0'}]

    json_packages = dumps(packages)
    json_copper = dumps(Copper)
    json_bronze = dumps(Bronze)
    json_silver = dumps(Silver)
    json_gold = dumps(Gold)
    json_platinum = dumps(Platinum)
    json_security_sensors = dumps(security_sensors)
    json_accessories = dumps(accessories)
    json_fire_sensors = dumps(fire_sensors)
    json_home_automation = dumps(home_automation)
    json_security_panels = dumps(security_panels)

    return dict(packages=packages,
                monitoring=monitoring,
                json_packages=json_packages,
                json_copper=json_copper,
                json_bronze=json_bronze,
                json_silver=json_silver,
                json_gold=json_gold,
                json_platinum=json_platinum,
                json_security_sensors=json_security_sensors,
                json_accessories=json_accessories,
                json_fire_sensors=json_fire_sensors,
                json_home_automation=json_home_automation,
                json_security_panels=json_security_panels)


@render_to('templates/dyntest.html')
def draw_test(request):
	return dict()
