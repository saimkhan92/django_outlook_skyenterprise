from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from tutorial.authhelper import get_signin_url
from tutorial.authhelper import get_signin_url, get_token_from_code, get_access_token
from tutorial.outlookservice import get_me, get_my_messages, get_top_messages, get_message_body
import time
import os
import 

# Create your views here.

def home(request):
  redirect_uri = request.build_absolute_uri(reverse('tutorial:gettoken'))
  sign_in_url = get_signin_url(redirect_uri)
  return HttpResponse('<a href="' + sign_in_url +'">Click here to sign in and view your mail</a>')

def gettoken(request):
  auth_code = request.GET['code']
  redirect_uri = request.build_absolute_uri(reverse('tutorial:gettoken'))
  token = get_token_from_code(auth_code, redirect_uri)
  access_token = token['access_token']
  user = get_me(access_token)
  refresh_token = token['refresh_token']
  expires_in = token['expires_in']

  # expires_in is in seconds
  # Get current timestamp (seconds since Unix Epoch) and
  # add expires_in to get expiration time
  # Subtract 5 minutes to allow for clock differences
  expiration = int(time.time()) + expires_in - 300

  # Save the token in the session
  request.session['access_token'] = access_token
  request.session['refresh_token'] = refresh_token
  request.session['token_expires'] = expiration
  #return HttpResponse('User: {0}, Access token: {1}'.format(user['displayName'], access_token))
  return HttpResponseRedirect(reverse('tutorial:download_mail'))                 #return HttpResponseRedirect(reverse('tutorial:saim_skyent_mail_body')) # add to urls.py also

def mail(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  # If there is no token in the session, redirect to home
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    messages = get_my_messages(access_token)
    #print("id: "+ str(type(messages["value"][0]["id"])))
    #print("body: "+ str(type(messages["value"][0]["body"]["content"])))
    #return HttpResponse('Messages: {0}'.format(messages["value"][0]["body"]["content"]))

    context = { 'messages': messages['value'] }
    return render(request, 'tutorial/mail.html', context)

def download_mail(request):
  access_token = get_access_token(request, request.build_absolute_uri(reverse('tutorial:gettoken')))
  if not access_token:
    return HttpResponseRedirect(reverse('tutorial:home'))
  else:
    messages = get_top_messages(access_token)
    #return HttpResponse('Messages: {0}'.format(messages))
    #context = { 'messages': messages['value'] }
    #return render(request, 'tutorial/mail.html', context)
    #return HttpResponse('Messages: {0}'.format(message_bodies))
    sky_ent_mail_id_list=[]
    sky_ent_mail_body_list=[]
    sky_ent_message_list=[]

    for message in messages["value"]:
      if message["subject"]=="Juniper Sky Enterprise: Successful device creation" and message["from"]["emailAddress"]["address"]=="saimkhan@juniper.net":
        sky_ent_mail_id_list.append(message["id"])
        sky_ent_message_list.append(message)
    #print(sky_ent_mail_id_list)

    for id in sky_ent_mail_id_list:
      body=get_message_body(access_token,id)
      sky_ent_mail_body_list.append(body)

    counter=0
    file_path=os.getcwd()+"/ztp/emails/"
    for body in sky_ent_mail_body_list:
      #print(body["body"]["content"])
      counter+=1
      file_name="file_"+str(counter)+".html"
      with open(file_path+file_name,"w") as fh:
        fh.write(body["body"]["content"])

    context = { 'messages': sky_ent_message_list }
    return render(request, 'tutorial/mail.html', context)
