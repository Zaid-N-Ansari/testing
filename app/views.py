from django.shortcuts import render

def home_view(request, *args, **kwargs):
	return render(request, 'app/home.html', {'user':False})
