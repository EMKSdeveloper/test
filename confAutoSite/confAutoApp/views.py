from confAutoApp.forms import TheForm
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from PyPDF2 import PdfFileWriter, PdfFileReader

whats_happening = " "
SCOPES = ['https://www.googleapis.com/auth/']

#loads and displays the form
#validates, cleans, and saves form data
#sends to "submitting" upon submitting the form
def index(request):
	template = get_template('confAutoApp/index.html').template

	form = TheForm(data=request.POST)
	if request.method == 'POST':
		form = TheForm(data=request.POST)
				
		if form.is_valid():
			form.save()
			cleaned_formdata = str(form.cleaned_data)
			request.session['which_task'] = str(form.cleaned_data['which_task'])
			request.session['original_file'] = str(form.cleaned_data['original_file'])
			request.session['split_files'] = str(form.cleaned_data['split_files'])
			request.session['grade_folder'] = str(form.cleaned_data['grade_folder'])
			return HttpResponseRedirect('submitting/')
	else:
		print(form.errors)
		form = TheForm()
		
	return render(request, 'confAutoApp/index.html', {'form': form})

#calls helper methods depending on which task was selected
#sends you back to a blank form when task is complete
def submitting(request):
	whats_happening = "submitting"
	formdata = request.session.get('formdata')
	split_pdf(request)
	form = TheForm()
	return render(request, 'confAutoApp/index.html', {'form': form})
	
#splits the PDF into individual files
#renames those files and saves them to a folder on your computer
#calls the function to upload files to google	
def split_pdf(request):
	gauth = GoogleAuth()
	gauth.LocalWebserverAuth()
	drive = GoogleDrive(gauth)

	originalFileLocation = request.session.get('original_file')
	splitFilesLocation = request.session.get('split_files')
	
	input_pdf = PdfFileReader(originalFileLocation)
	numOfPages = input_pdf.getNumPages()

	#for x in range(5):
	for x in range(numOfPages):
		output = PdfFileWriter()
		thisPage = input_pdf.getPage(x)
		stringOfText = thisPage.extractText()
		studentName = getName(stringOfText)
		studentGrade = getGrade(stringOfText)
		studentCohort = getCohort(stringOfText)
		output.addPage(thisPage)
		studentName = studentName.replace("'", "_")
		if (request.session.get('which_task')=='SSRC'):
			fileString = studentGrade + " (" + studentCohort + ") - " + studentName + " Report Card.pdf"
		if (request.session.get('which_task')=='SSSP'):
			fileString = studentGrade + " (" + studentCohort + ") - " + studentName + " Supplemental Page.pdf"
		request.session['fileString'] = fileString
		outputFileName = os.path.join(splitFilesLocation, fileString)
		request.session['fullFileName'] = outputFileName
		request.session['folderId'] = getFolderId(request)
		with open(outputFileName, "wb") as output_stream:
			output.write(output_stream)
		drive = uploadToGoogle(request, drive)

#ID google folder with matching name
def findGoogleFolder(request, service, gcreds):
	page_token = None
	folderList = service.files().list(
		q = "mimeType='application/vnd.google-apps.folder'",
		spaces = "drive",
		fields = 'nextPageToken, files(id, name)',
		pageToken = page_token).execute()
	print(folderList)
	return service

#upload file to correct google folder
def uploadToGoogle(request, drive):
	fileName = request.session.get('fileString')
	fileLocation = request.session.get('fullFileName')
	
	gfile = drive.CreateFile({'title': fileName, 'parents': [{'id': request.session.get('folderId')}]})
	gfile.SetContentFile(fileLocation)
	gfile.Upload()
	gfile = None
	return drive

def getFolderId(request):
	gradeGoogleFolder = request.session.get('grade_folder')

	stringList = gradeGoogleFolder.split(r"/")
	stringList.reverse()
	containsFolderId = stringList[0]
	if containsFolderId.count("?") != 0:
		stringList = containsFolderId.split("?")
		folderId = stringList[0]
	else:
		folderId = containsFolderId
	return folderId

def getName(stringName):
	stringList = stringName.split(r"3/11/22")
	containsName = stringList[1]
	#containsName = removeColon(containsName)
	nameString = containsName.split("Grade")
	strippedName = nameString[0].strip(" \n")
	return strippedName

def getGrade(stringName):
	stringList = stringName.split("Grade: ")
	containsGrade = stringList[1]
	#containsGrade = removeColon(containsGrade)
	gradeString = containsGrade.split("Cohort: ")
	return gradeString[0]

def getCohort(stringName):
	stringList = stringName.split("Cohort: ")
	containsCohort = stringList[1]
	#containsCohort = removeColon(containsCohort)
	cohortString = containsCohort.split("Class")
	return cohortString[0]

def removeColon(subString):
	containsColon = subString.find(":")
	if containsColon != -1:
		list2 = subString.split(":")
		subString = list2[0]
	return subString
