from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def home(request):
  sign_in_url = '#'
  context = { 'signin_url': sign_in_url }
  return render(request, 'tutorial/home.html', context)
# Create your views here.
