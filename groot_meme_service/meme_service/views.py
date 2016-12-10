from django.http import HttpResponse, HttpResponseBadRequest
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from models import Meme, User
import json
import random

# Create your views here.

def browse(request):
    try:
        indices = random.sample(xrange( Meme.objects.count() ), 10)
    except ValueError:
        indices = range(0, Meme.objects.count() )
    meme_objects = []
    for index in indices:
        current_meme = Meme.objects.all()[index]
        meme_objects.append( {'user': current_meme.user, 'url': current_meme.url, 'score': current_meme.score} )
    return HttpResponse(json.dumps(meme_objects))

def query(request):
    if request.method == 'GET' and 'user' in request.GET:
        filtered = Meme.objects.filter( user=request.GET['user'] )
        index = random.randint(0, filtered.count()-1)
        meme_object = {'user': filtered[index].user, 'url': filtered[index].url, 'score': filtered[index].score}
        return HttpResponse(json.dumps(meme_object))
    return HttpResponseBadRequest()

def upload(request):
    if request.method == 'POST' and 'user' in request.POST and 'url' in request.POST:
        # validate url
        val = URLValidator(verify_exists=True)
        try:
            val(request.POST['url'])  # throws ValidationError if url does not exist
        except ValidationError, e:
            return HttpResponseBadRequest()
        meme_object = Meme(user=request.POST['user'], score=0, url=request.POST['url'])
        meme_object.save()
        return HttpResponse(status=200)
    return HttpResponseBadRequest()
