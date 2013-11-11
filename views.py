from annoying.decorators import render_to, ajax_request

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


@render_to('templates/dyntest.html')
def draw_test(request):
	return dict()