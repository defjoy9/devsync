# mysite/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')  # redirect to login after registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
