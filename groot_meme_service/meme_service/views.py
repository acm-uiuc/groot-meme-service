from django.http import HttpResponse
from models import Meme, User

# Create your views here.

def browse(request):
    return HttpResponse("Browse endpoint")

def query(request):
    if 'user' in request.GET:
        return HttpResponse("User requested meme from user %s" % request.GET['user'])
    return HttpResponse("Bad request")

def upload(request):
    return HttpResponse("Upload endpoint")
