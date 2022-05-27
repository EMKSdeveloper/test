from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from confAutoApp.models import Locations

class TheForm(forms.ModelForm):
	which_task = forms.ChoiceField(label="Task You Want to Perform", required="true", 
		choices=Locations.TASK_CHOICES)
	grade = forms.ChoiceField(label="Grade", required="true", 
		choices=Locations.GRADE_CHOICES)
	original_file = forms.CharField(label="File Location of the Master Document", required="true")
	split_files = forms.CharField(label="File Location Where Individual Files Can Be Saved", required="true")
	grade_folder = forms.CharField(label="Google Drive Link Where Individual Files Can Be Saved", required="true")

	class Meta:
		model = Locations
		fields = ['which_task', 'grade', 'original_file', 'split_files', 'grade_folder']
