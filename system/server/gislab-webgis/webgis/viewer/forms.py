from django import forms
#from django.forms.widgets import SelectMultiple


class MultipleStringsField(forms.CharField):
	"""Form field that accepts multiple values given as comma separated
	string (?param=val1,val2)."""

	#widget = SelectMultiple

	def to_python(self, value):
		if value:
			return [item.strip() for item in value.split(",")] # remove padding
		return []

class MultipleIntegersField(forms.CharField):
	"""Form field that accepts multiple integer values given as comma separated
	string (?param=val1,val2)."""

	#widget = SelectMultiple

	def to_python(self, value):
		if value:
			return [int(item) for item in value.split(",")] # remove padding
		return []


class ViewerForm(forms.Form):
	project = forms.CharField(required=False)
	osm = forms.CharField(required=False)
	google = forms.CharField(required=False)
	layers = MultipleStringsField(required=False)
	visible = MultipleStringsField(required=False)
	dpi = forms.IntegerField(required=False)
	scales = MultipleIntegersField(required=False)
	extent = forms.CharField(required=False)
	drawings = MultipleStringsField(required=False)
