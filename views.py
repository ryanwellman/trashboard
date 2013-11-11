from annoying.decorators import render_to, ajax_request
from django.core.serializers.json import DjangoJSONEncoder
import json
from json import dumps

@render_to('templates/container.html')
def draw_container(request):
	ctx	=	{	'name': "Joe Blow",
				'address': "3490 Jeffro Lane",
				'city': "Austin",
				'state': "Texas",
				'zip': "78728"
			}

	# uses render_to to draw the template
	return dict(customer=ctx)


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
