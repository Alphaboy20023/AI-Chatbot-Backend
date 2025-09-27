from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import *

# class RegisterView(APIView):
#     def post(self, request):
#         serializer = RegisterUserSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response({
#             "id": user.id,
#             "email": user.email,
#             "username": user.username,
#         }, status=status.HTTP_201_CREATED)


# In your app's views.py
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("App routing works!")


