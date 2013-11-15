# import built-ins
import json
from json import dumps, loads
from random import choice

# import 3rd-party modules
from annoying.decorators import render_to, ajax_request
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.views.decorators.csrf import csrf_exempt
from dynamicresponse.response import *

# import from self (models)
from agreement.models import Agreement

@csrf_exempt
def dyn_json(request, agreement_id=None):
    # attempts to get or set a specific agreement
    # this is csrf_exempt so i can test it with curl
    agreement = None
    blob = {}

    if agreement_id:
        # user wants a specific agreement
        agreement = get_object_or_404(Agreement.objects.all(), pk=agreement_id)
        blob = agreement.serialize()
    
    if request.method == 'POST':
        for key in request.POST:    # request.POST is fucked up when sending JSON
            incoming = loads(key)

        # does blob exist?
        if blob:
            # we are updating an existing one
            agreement.update_from_dict(incoming)
        else:
            # we are creating a new one so obtain json from post
            blob = incoming

            # create and save it
            agreement = Agreement.objects.create(**blob)
            agreement.save()

    return SerializeOrRedirect(reverse(draw_test), blob)


def serve_json(request):
    # returns a random agreement as json
    agreement = Agreement.objects.order_by('?')[0]
    # this next one will be better as soon as there are any objects in the database
    # agreement = Agreement.objects.raw('SELECT * FROM agreement_agreement ORDER BY RAND() LIMIT 1')

    ctx = agreement.serialize()
    return SerializeOrRedirect(reverse(draw_test), ctx)


@render_to('templates/container.html')
def draw_container(request):
    # uses render_to to draw the template

    # this is a dummy view that will render a dummy form that is simply to demo
    # the possibilities that come with the new agreement form

    # in reality these values would be coming from the models in pricemodels.py
    # right now there is no actual Agreement model other than the dummy one in the
    # agreement app

    # for the following 4 lists of dictionaries:
    # from PTblProduct: name <-> name, description <-> description, price <-> price
    premiums    =  [    {'name':'Camera Add-on', 'price':'$49.99', 'description': 'Watch your home from somewhere else!'},
                        {'name':'Cellular Service', 'price':'$79.99', 'description': 'Cut the wires and it still works!'},
                        {'name':'GPS', 'price':'$99.99', 'description': 'Let first responders know where you are at all times!'}    ]

    combos      =  [    {'name':'3 Keypads', 'price':'$99.99', 'description': 'Great for households with children!'},
                        {'name':'Many Keychains', 'price':'$29.99', 'description': 'So cheap they\'re disposable!'},
                        {'name':'Solar Alarm Add-on Kit', 'price':'$159.99', 'description': 'For the consumer with no grid power!'}    ]

    services    =  [    {'name':'Video Service', 'price':'$19.99/mo', 'reason': 'cameras'},
                        {'name':'Smoke Service', 'price':'$29.99/mo', 'reason': 'smoke detector(s)'},
                        {'name':'Alpaca Rental Service', 'price':'$159.99/mo', 'reason': 'alpaca shears'}    ]

    closers     =  [    {'name': '$5/mo rate drop', 'description': 'Removes $5 from the monthly monitoring rate'},
                        {'name': '$10/mo rate drop', 'description': 'Removes $10 (requires manager approval)'},
                        {'name': 'Free Keychains', 'description': 'Give away some of our famous disposable keychains'},
                        {'name': 'Free Shipping', 'description': 'Cancels out shipping cost for the customer'}  ]

    # this one is going to come from the Package class and will change later
    packages    =  [    {'name':'Copper', 'price':'$19.99/mo', 'xt':'1', 'dw':'3', 'mot':'1'},
                        {'name':'Bronze', 'price':'$35.99/mo', 'xt':'1', 'dw':'7', 'mot':'1'},
                        {'name':'Silver', 'price':'$37.99/mo', 'xt':'1', 'dw':'10', 'mot':'1'},
                        {'name':'Gold', 'price':'$39.99/mo', 'xt':'1', 'dw':'12', 'mot':'1'},
                        {'name':'Platinum', 'price':'$42.99/mo', 'xt':'1', 'dw':'15', 'mot':'1'}    ]
    
    return dict(premiums=premiums, combos=combos, services=services, closers=closers, packages=packages)


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
