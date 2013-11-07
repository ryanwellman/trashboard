from annoying.decorators import render_to, ajax_request

@render_to('templates/container.html')
def draw_container(request):

	# uses render_to to draw the template
	return dict()