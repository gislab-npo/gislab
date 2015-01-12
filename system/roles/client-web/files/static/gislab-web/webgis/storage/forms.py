from django import forms

from webgis.libs.forms import CaseInsensitiveForm, CaseInsensitiveModelForm
from webgis.storage.models import Ball, Drawing


class GetBallForm(CaseInsensitiveForm):
	id = forms.ModelChoiceField(queryset=Ball.objects.all(), help_text=u"Ball ID.")

class BallDataForm(CaseInsensitiveModelForm):
	class Meta:
		model = Ball
		fields = ["data", "mime_type"]


class DrawingRecordForm(CaseInsensitiveModelForm):
	class Meta:
		model = Drawing

class DrawingHistoryForm(CaseInsensitiveForm):
	user = forms.CharField(required=True)
	project = forms.CharField(required=False)
	start = forms.IntegerField(min_value=0, required=False)
	limit = forms.IntegerField(min_value=1, required=False)
