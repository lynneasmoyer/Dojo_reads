from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import *
import bcrypt

def index(request):
    return render(request, 'login_app/index.html')

def success(request):
    if request.method == 'GET':
        if 'user_id' in request.session:
            return render(request, 'login_app/books.html')
        else:
            return redirect('/')

def register(request):
    if request.method == "POST":
        errors = User.objects.basic_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')
        else:
            pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()) 
            new_user= User.objects.create(
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email'],
                password = pw_hash
            )
            request.session['user_id'] = new_user.id 
            request.session['first_name'] = new_user.first_name
            return redirect('/books')

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email=request.POST['email'])
        if user:
            logged_user = user[0]
            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                request.session['user_id'] = logged_user.id
                return redirect('/books')
        else:
            messages.error(request, 'Account not found. Register now!')
            return redirect('/')


def logout(request):
    if request.method == 'GET':
        request.session.clear()
    return redirect('/')

def books(request):
    context = {
        'reviews': Review.objects.all().order_by('-created_at'),
        'user': User.objects.get(id=request.session['user_id'])
    }
    print(Review.objects.all())
    print(User.objects.get(id=request.session['user_id']))
    return render(request, 'login_app/books.html', context)

def add_book(request):
    context = {
        'authors': Author.objects.all(),
        'user': User.objects.get(id=request.session['user_id'])
    }
    return render(request, 'login_app/add_book.html', context)

def create_review(request):
    if request.method == 'POST':
        author= Author.objects.create(name=request.POST['author'])
        book = Book.objects.create(title=request.POST['title'], author=author)
        user = User.objects.get(id=request.session['user_id'])
        print("*********", user.first_name)
        Review.objects.create(content=request.POST['content'],rating=int(request.POST['rating']),book= book,user= user)
    return redirect('/books')