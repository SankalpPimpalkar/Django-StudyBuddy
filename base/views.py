from django.shortcuts import render,redirect
from .models import Room,Topic,Message
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
            return redirect('login_page')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Wrong password")
        
    context = {'page':page}
    return render(request, 'login_register.html', context)

def registerPage(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Failed to create user')
    context = {
        'page':page,
        'form':form,
    }
    return render(request, 'login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login_page')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.all()
    
    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
    }
    
    return render(request, 'home.html', context) 

def room(request, pk):
    
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    
    if request.method == "POST":
        Message.objects.create(
            user= request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room_page', pk=room.id)
    
    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }
    
    return render(request, 'room.html', context)

@login_required(login_url='login_page')
def createRoom(request):
    
    form = RoomForm()
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'room_form.html', context)

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse('You are not creator')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'room_form.html', context)

def deleteRoom(request,pk):
    page = 'room'
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'delete.html', {'page': page})

@login_required(login_url='login_page')
def deleteMessage(request, pk):
    room_message = Message.objects.get(id=pk)
    page = f"'{room_message.body}'"

    if request.user != room_message.user:
        return HttpResponse('You are not creator of this message')
    
    if request.method == 'POST':
        room_message.delete()
        return redirect('room_page')
    
    return render(request, 'delete.html', {'page': page})