# users\views.py
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
import json

from .models import CustomUser
from .serializers import CustomUserSerializer

# Create your views here.
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.order_by('-id')
    serializer_class = CustomUserSerializer

def get_user(request):           
    user = CustomUser.objects.get(id=request.user.id)
    json_user = json.dumps({'first_name':user.first_name, 'id':user.id, 'last_name':user.last_name}, ensure_ascii=False)
    return HttpResponse(json_user)