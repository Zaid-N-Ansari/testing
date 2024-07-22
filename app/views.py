from django.shortcuts import render
from account.forms import SearchUserForm

def home_view(request, *args, **kwargs):
	form = SearchUserForm()
	return render(request, 'app/home.html', {'user':False, 'form':form})
