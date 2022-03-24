from django.shortcuts import render
from django.http import JsonResponse
import random
import time
from agora_token_builder import RtcTokenBuilder
from .models import RoomMember
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from mychat import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token


# Create your views here.
def home(request):
    return render(request, 'base/signin.html')

def signup(request):

    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request,"Username already exist! Please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"Email already registered")
            return redirect('home')

        if len(username)>10:
            messages.error(request,"Username must be under 10 characters")

        if pass1 != pass2:
            messages.error(request,"Passwords didn't match!!")
        
        if not username.isalnum():
            messages.error(request,"Username must be alpha numeric !! ")
            return redirect('home')





        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = True
        myuser.save()
 
        messages.success(request, "Your Account has been successfully created. We've sent you a confirmation email, please confirm your email in order to activate your account.")

        # welcome email

        subject = "Welcome to iNeuron Challenge-4"
        message = "Hi " + myuser.first_name + " !! \n" + "You'll get another mail for email verification, please verify there to Activate your account !! \n\n" + "Thanks for your interest in checking my i neuron Challenge-4 Django Video Conference App Submission. \n\n" + "Kindly Wish me Good Luck --- Sai Kumar Reddy Korsapati."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Confirmation 

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ iNeuron Challenge4"
        message2 = render_to_string('email_confirmation.html',{
            'name' : myuser.first_name,
            'domain' : current_site.domain,
            'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token' : generate_token.make_token(myuser)
        })

        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email],)
        email.fail_silently = True
        email.send()


        return redirect('signin')

    return render(request, 'base/signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username = username, password = pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, 'base/lobby.html', {'fname': fname})
        else:
            messages.error(request,'Bad Credentials')
            return redirect('home')

    return render(request, 'base/signin.html')

def signout(request):
    logout(request)
    messages.success(request,"Logged Out Successfully")
    return redirect('home')
    # return render(request, 'base/signout.html')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')

def lobby(request):
    return render(request, 'base/lobby.html')

def room(request):
    return render(request, 'base/room.html')


def getToken(request):
    appId = "03f0a8e0010543679159caa866ff5b99"
    appCertificate = "6a11ffbab3594f7e9be3749bd575d9c3"
    channelName = request.GET.get('channel')
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

    return JsonResponse({'token': token, 'uid': uid}, safe=False)


@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )

    return JsonResponse({'name':data['name']}, safe=False)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({'name':member.name}, safe=False)

@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    member = RoomMember.objects.get(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )
    member.delete()
    return JsonResponse('Member deleted', safe=False)