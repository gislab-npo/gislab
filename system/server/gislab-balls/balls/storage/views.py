from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from balls.storage import forms
from balls.storage.models import Ball


def _get_file_extension(mime_type):
	mime_type = mime_type.split(";")[0].strip()
	return settings.FILE_EXTENSIONS_TABLE.get(mime_type, "txt")


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
			response['Content-Disposition'] = 'attachment; filename={0}.{1}'.format(ball.id, _get_file_extension(ball.mime_type))
			return response
	raise Http404
