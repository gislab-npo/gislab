from django import forms

from webgis.storage.models import Ball, Drawing


class GetBallForm(forms.Form):
	ID = forms.ModelChoiceField(queryset=Ball.objects.all(), help_text=u"Ball ID.")


class BallDataForm(forms.ModelForm):
	class Meta:
		model = Ball
		fields = ["data", "mime_type"]


class DrawingRecordForm(forms.ModelForm):
	class Meta:
		model = Drawing

class DrawingHistoryForm(forms.Form):
	user = forms.CharField(required=True)
	project = forms.CharField(required=True)
	start = forms.IntegerField(min_value=0, required=False)
	limit = forms.IntegerField(min_value=1, required=False)
