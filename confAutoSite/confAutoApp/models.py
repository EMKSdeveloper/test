from django.db import models

# Create your models here.
class Student(models.Model):
	name = models.CharField(max_length = 200)
	cohort = models.CharField(max_length = 200)
	grade = models.IntegerField(default = 0)

	def __str__(self):
		return self.name
	


class Locations(models.Model):
	TASK_CHOICES = [
		('SSRC', 'Split and Sort Report Cards'),
		('SSSP', 'Split and Sort Supplemental Pages'),
	]
	GRADE_CHOICES = [
		('FIVE', '5'),
		('SIX', '6'),
		('SEVEN', '7'),
		('EIGHT', '8'),
		('NINE', '9'),
		('TEN', '10'),
		('ELEVEN', '11'),
		('TWELVE', '12'),
	]

	which_task = models.CharField(max_length = 200, choices = TASK_CHOICES, default = ' ')
	grade = models.CharField(max_length = 200, choices = GRADE_CHOICES, default = ' ')
	original_file = models.TextField(default=' ', max_length = 200)
	split_files = models.TextField(default=' ', max_length = 200)
	grade_folder = models.TextField(default=' ', max_length = 200)

	def __str__(self):
		return self.which_task


