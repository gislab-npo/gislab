from django import forms

from balls.storage.models import Ball


class GetBallForm(forms.Form):
	ID = forms.ModelChoiceField(queryset=Ball.objects.all(), help_text=u"Ball ID.")


class BallDataForm(forms.ModelForm):
	class Meta:
		model = Ball
		fields = ["data", "mime_type"]
