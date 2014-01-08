from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from balls.balls import forms
from balls.balls.models import Ball


@csrf_exempt
def ball(request):
	if request.method == "POST":
		form = forms.BallDataForm({'data': request.body, 'mime_type': request.environ['CONTENT_TYPE']})
		if form.is_valid():
			ball = form.save()
			return HttpResponse(ball.id)
	else:
		form = forms.GetBallForm(request.GET)
		if form.is_valid():
			ball = form.cleaned_data["ID"]
			response = HttpResponse(ball.data, content_type=ball.mime_type)
			response['Content-Disposition'] = 'attachment; filename=ball-{0}.txt'.format(ball.id)
			return response
	raise Http404
