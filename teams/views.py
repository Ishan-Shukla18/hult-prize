import uuid, csv
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import HttpResponse, redirect, render
from .models import Team, TeamMember, Faq, Speaker
from datetime import datetime

def home(request):
    # if request.user.is_authenticated and Team.objects.filter(user=request.user).first().is_leader == False:
    #     return redirect('/join-team')
    # if request.user.is_authenticated:
    #     return redirect('/create-team')
    return render(request, 'home.html')

def team(request):
    if request.user.is_authenticated and Team.objects.filter(user=request.user).first().is_leader == False:
        return redirect('/join-team')
    if request.user.is_authenticated:
        return redirect('/create-team')
    else:
        return redirect('/')

def createTeam(request):
    if request.method == "POST":
        team_name = request.POST.get('team_name')
        update_team_name = Team.objects.filter(user=request.user).first()
        update_team_name.team_name = team_name
        update_team_name.save()
        fname1 = request.POST.get('fname-1')
        lname1 = request.POST.get('lname-1')
        email1 = request.POST.get('email-1').strip()
        phone1 = request.POST.get('phone-1')
        fname2 = request.POST.get('fname-2')
        lname2 = request.POST.get('lname-2')
        email2 = request.POST.get('email-2').strip()
        phone2 = request.POST.get('phone-2')
        fname3 = request.POST.get('fname-3')
        lname3 = request.POST.get('lname-3')
        email3 = request.POST.get('email-3').strip()
        phone3 = request.POST.get('phone-3')
        teamKey = Team.objects.filter(user=request.user).first()
        if ((email1 == '' and email2 == '' and email3 == '') or (phone1 == '' and phone2 == '' and phone3 == '')) and Team.objects.filter(user=request.user).first().is_leader == True:
            messages.warning(request, 'Team deleted. Now you can join other team or create again')
            TeamMember.objects.filter(team=teamKey).all().delete()
            is_team_leader = Team.objects.filter(user=request.user).first()
            is_team_leader.is_leader = False
            is_team_leader.save()
            return redirect('/join-team')
        if (email1 == '' and email2 == '' and email3 == '') or (phone1 == '' and phone2 == '' and phone3 == ''):
            messages.error(request, 'Atleast two members are required')
            return redirect('/create-team')
        if ((email1 != '' and (email1 == email2 or email1 == email3)) or (email2 != '' and (email2 == email1 or email2 == email3)) or (email3 != '' and (email3 == email1 or email3 == email2)) or (email1 == teamKey.user.email or email2 == teamKey.user.email or email3 == teamKey.user.email)):
            messages.error(request, 'Email cannot be same')
            return redirect('/create-team')
        TeamMember.objects.filter(team=teamKey).all().delete()
        teamMember1 = TeamMember(team=teamKey, first_name=fname1, last_name=lname1, email=email1, phone_no=phone1)
        teamMember2 = TeamMember(team=teamKey, first_name=fname2, last_name=lname2, email=email2, phone_no=phone2)
        teamMember3 = TeamMember(team=teamKey, first_name=fname3, last_name=lname3, email=email3, phone_no=phone3)
        teamMember1.save()
        teamMember2.save()
        teamMember3.save()
        is_team_leader = Team.objects.filter(user=request.user).first()
        is_team_leader.is_leader = True
        is_team_leader.save()
        messages.success(request, 'Data has been successfully saved')
        return redirect('/create-team')
    if request.user.is_authenticated:
        team = Team.objects.filter(user=request.user).first()
        team_members = TeamMember.objects.filter(team=team).all()
        return render(request, 'create-team.html', { 'team_members': team_members, 'team': team })
    else:
        return redirect('/')

def handleLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.error(request, 'User not found')
            return redirect('/login')
        team_obj = Team.objects.filter(user=user_obj).first()
        if not team_obj.is_verified:
            messages.info(request, 'Profile is not verified yet. Please check your mail')
            return redirect('/login')
        user = authenticate(username=username, password=password)
        if user is None:
            messages.error(request, 'Wrong password or username')
            return redirect('/login')
        login(request, user)
        if Team.objects.filter(user=request.user).first().is_leader == False:
            return redirect('/join-team')
        else:
            return redirect('/create-team')
    else:
        if request.user.is_authenticated:
            if Team.objects.filter(user=request.user).first().is_leader == False:
                return redirect('/join-team')
            else:
                return redirect('/create-team')
        else:
            return render(request, 'login.html')

def handleLogout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect('/')
    else:
        return HttpResponse("404 - Page not found")

def handleSignUp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone_no = request.POST.get('phone-no')
        try:
            if User.objects.filter(username=username).first():
                messages.warning(request, 'Username is already taken')
                return redirect('/signup')
            if User.objects.filter(email=email).first():
                messages.warning(request, 'Email is already taken.')
                return redirect('/signup')
            if password1 != password2:
                messages.warning(request, 'Passwords do not match')
                return redirect('/signup')
            user =  User.objects.create_user(username, email, password1)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            auth_token = str(uuid.uuid4())
            team = Team(user=user, auth_token=auth_token, leader_phone_no=phone_no, is_leader=False)
            team.save()
            sendMail(email, auth_token)
            return redirect('/token')
        except Exception as e:
            messages.error(request, 'Error occured')
            return redirect('/')
    else:
        if request.user.is_authenticated:
            return redirect('/create-team')
        else:
            return render(request, 'signup.html')

def token(request):
    return render(request, 'token.html')

def sendMail(email, token):
    subject = 'Verify your account - Hult Prize'
    message = f'Please click the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def verify(request, auth_token):
    try:
        team_obj = Team.objects.filter(auth_token=auth_token).first()
        if team_obj:
            if team_obj.is_verified:
                messages.success(request, 'Your account is already verified')
                return redirect('/')
            team_obj.is_verified = True
            team_obj.save()
            messages.success(request, 'Your account has been verified')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        return redirect('/')

def teamsCSV(request):
    if request.user.username == 'admin':
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="teams.csv"'
        writer = csv.writer(response)
        writer.writerow(
                [
                    "Team name",
                    "Team Members",
                    "Email",
                    "Phone No."
                ]
            )
        for team in Team.objects.all():
            writer.writerow(
                [
                    team.team_name,
                    team.user.first_name + " " + team.user.last_name + " " + "(Leader)",
                    team.user.email,
                    team.leader_phone_no
                ]
            )
            team_members = TeamMember.objects.filter(team=team).all()
            for team_member in team_members:
                writer.writerow(
                    [
                        team.team_name,
                        team_member.first_name + " " + team_member.last_name,
                        team_member.email,
                        team_member.phone_no
                    ]
                )
            writer.writerow([])
        return response
    else:
        return redirect('/')

def faqs(request):
    faqs = Faq.objects.all()
    return render(request, 'faqs.html', { 'faqs': faqs })

def speakers(request):
    speakers = Speaker.objects.all()
    return render(request, 'speakers.html', { 'speakers': speakers })

def joinTeam(request):
    if request.method == 'POST':
        if Team.objects.filter(user=request.user).first().is_leader == False:
            auth_token = request.POST.get('auth_token')
            team = Team.objects.filter(auth_token=auth_token).first()
            team_from = Team.objects.filter(user=request.user).first()
            team_leader_email = team.user.email
            if team_from.can_request == True:
                subject = 'Request to join your team'
                message = f'{request.user.first_name + " " + request.user.last_name} would like to join your team.\nClick on the link to add - http://127.0.0.1:8000/accept-invitation/{Team.objects.filter(user=request.user).first().auth_token}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [team_leader_email]
                send_mail(subject, message, email_from, recipient_list)
                team_from.can_request = False
                team_from.can_request_timestamp = datetime.now()
                team_from.save()
                messages.success(request, 'Your request has been sent')
                return redirect('/join-team')
            else:
                team_timestamp = team_from.can_request_timestamp.date()
                date_now = datetime.now().date()
                delta = date_now - team_timestamp
                if delta.days >= 1:
                    subject = 'Request to join your team'
                    message = f'{request.user.first_name + " " + request.user.last_name} would like to join your team.\nClick on the link to add - http://127.0.0.1:8000/accept-invitation/{Team.objects.filter(user=request.user).first().auth_token}'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [team_leader_email]
                    send_mail(subject, message, email_from, recipient_list)
                    team_from.can_request = False
                    team_from.can_request_timestamp = datetime.now()
                    team_from.save()
                    messages.success(request, 'Your request to join the team has been sent. Please wait for the leader to accept it')
                    return redirect('/join-team')
                messages.error(request, 'Request can been sent only once in 24 hours')
                return redirect('/join-team')
        else:
                messages.warning(request, 'You are Team Leader so you cannot join other team. Remove all members from your team to be able join other teams')
                return redirect('/join-team')
    else:
        if request.user.is_authenticated:
            teams = Team.objects.exclude(user=request.user)
            data = []
            team_from = Team.objects.filter(user=request.user).first()
            team_timestamp = team_from.can_request_timestamp.date()
            date_now = datetime.now().date()
            delta = date_now - team_timestamp
            if delta.days >= 1:
                team_from.can_request = True
                team_from.can_request_timestamp = datetime.now()
                team_from.save()
            for team in teams:
                team_member = TeamMember.objects.filter(team=team).all()
                data.append({
                    'team_name':team.team_name,
                    'leader': team.user.first_name + " " + team.user.last_name,
                    'auth_token': team.auth_token,
                    'team_member': team_member,
                    'is_leader': Team.objects.filter(user=request.user).first().is_leader,
                    'can_request': Team.objects.filter(user=request.user).first().can_request
                })
                return render(request, 'join-team.html', { 'data': data })
        else:
            return redirect('/')

def myTeam(request):
    if request.user.is_authenticated:
        myData = TeamMember.objects.filter(email=request.user.email).first()
        if myData is None:
            myData = Team.objects.filter(user=request.user).first()
            team_data = TeamMember.objects.filter(team=myData)
            team_name = myData.team_name
            team_leader = myData.user.first_name + " " + myData.user.last_name
            data = []
            data.append({
                'team_name': team_name,
                'team_leader': team_leader,
                'team_members': team_data
            })
        else:
            team_data = TeamMember.objects.filter(team=myData.team)
            team_leader = myData.team.user.first_name + " " + myData.team.user.last_name
            team_name = myData.team.team_name
            data = []
            data.append({
                'team_name': team_name,
                'team_leader': team_leader,
                'team_members': team_data
            })
        return render(request, 'my-team.html', { 'my_team': data })
    else:
        return redirect('/')

def acceptInvitation(request, auth_token):
    if request.user.is_authenticated:
        data = Team.objects.filter(auth_token=auth_token).first()
        team = Team.objects.filter(user=request.user).first()
        c = 0
        for i in TeamMember.objects.filter(team=team):
            if len(i.email) != 0:
                c = c + 1
        if c < 3:
            TeamMember(team=team, first_name=data.user.first_name, last_name=data.user.last_name, phone_no=data.leader_phone_no, email=data.user.email).save()
            for i in TeamMember.objects.filter(team=team):
                if len(i.email) == 0:
                    i.delete()
            left = 3 - TeamMember.objects.filter(team=team).count()
            while left > 0:
                left = left - 1
                TeamMember(team=team, first_name='', last_name='', phone_no='', email='').save()
            team.is_leader = True
            team.save()
            subject = 'Request accepted - Hult Prize'
            message = f'Your request to join the team has been accepted'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [Team.objects.filter(auth_token=auth_token).first().user.email]
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, 'Member added successfully')
            return redirect('/create-team')
        else:
            messages.error(request, '4 Membes already in the team')
            return redirect('/create-team')
    else:
        messages.error(request, 'Please login first to add team member')
        return redirect('/login')
