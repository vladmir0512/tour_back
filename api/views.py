from rest_framework.decorators import api_view
from rest_framework.response import Response
from route.models import Route, Comment, User
from rest_framework import serializers
from rest_framework import status
from .serializers import RouteSerializer, CommentSerializer, UserSerializer
from django.shortcuts import get_object_or_404

#-----------------------ROUTES---------------------------------
#-info---------------------------------------------------------
@api_view(['GET'])
def ApiRouteOverview(request):
	api_urls = {
		'all_routes': '/list',
		'Add': '/create',
		'Update': '/update/pk',
		'Delete': '/route/pk/delete'
	}

	return Response(api_urls)

#-create-------------------------------------------------------
@api_view(['POST'])
def add_route(request):
    route = RouteSerializer(data=request.data)

    # validating for already existing data
    if Route.objects.filter(**request.data).exists():
        raise serializers.ValidationError('This data already exists')

    if route.is_valid():
        route.save()
        return Response(route.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

#-update-------------------------------------------------------    
@api_view(['POST'])
def update_route(request, pk):
    route = Route.objects.get(pk=pk)
    data = RouteSerializer(instance=route, data=request.data)

    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

#-delete-------------------------------------------------------    
@api_view(['DELETE'])
def delete_route(request, pk):
    route = get_object_or_404(Route, pk=pk)
    route.delete()
    return Response(status=status.HTTP_202_ACCEPTED)
    
#-all----------------------------------------------------------    
@api_view(['GET'])
def view_routes(request):

    # checking for the parameters from the URL
    if request.query_params:
        route = Route.objects.filter(**request.query_params.dict())
    else:
        routes = Route.objects.all()

    # if there is something in items else raise error
    if routes:
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    
#-----------------------СOMMENTS-------------------------------
#-info---------------------------------------------------------
@api_view(['GET'])
def ApiCommentOverview(request):
	api_urls = {
		'all_comments': '/list',
		'Add': '/create',
		'Update': '/update/pk',
		'Delete': '/delete/pk'
	}

	return Response(api_urls)

#-create-------------------------------------------------------
@api_view(['POST'])
def add_comment(request):
    comment = CommentSerializer(data=request.data)

    # validating for already existing data
    if Comment.objects.filter(**request.data).exists():
        raise serializers.ValidationError('This data already exists')

    if comment.is_valid():
        comment.save()
        return Response(comment.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
#-update-------------------------------------------------------    
@api_view(['POST'])
def update_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    data = CommentSerializer(instance=comment, data=request.data)

    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

#-delete-------------------------------------------------------    
@api_view(['DELETE'])
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return Response(status=status.HTTP_202_ACCEPTED)
        
#-all----------------------------------------------------------        
@api_view(['GET'])
def view_comments(request):

    # checking for the parameters from the URL
    if request.query_params:
        comment = Comment.objects.filter(**request.query_params.dict())
    else:
        comments = Comment.objects.all()

    # if there is something in items else raise error
    if comments:
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
#-------------------------USERS--------------------------------
#-info---------------------------------------------------------
@api_view(['GET'])
def ApiUserOverview(request):
	api_urls = {
		'all_users': '/list',
		'Add': '/create',
		'Update': '/update/pk',
		'Delete': '/delete/pk'
	}

	return Response(api_urls)

#-create-------------------------------------------------------
@api_view(['POST'])
def add_user(request):
    user = UserSerializer(data=request.data)

    # validating for already existing data
    if User.objects.filter(**request.data).exists():
        raise serializers.ValidationError('This data already exists')

    if user.is_valid():
        user.save()
        return Response(user.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
#-update-------------------------------------------------------    
@api_view(['POST'])
def update_user(request, pk):
    user = User.objects.get(pk=pk)
    data = UserSerializer(instance=user, data=request.data)

    if data.is_valid():
        data.save()
        return Response(data.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

#-delete-------------------------------------------------------    
@api_view(['DELETE'])
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return Response(status=status.HTTP_202_ACCEPTED)
        
#-all----------------------------------------------------------        
@api_view(['GET'])
def view_users(request):

    # checking for the parameters from the URL
    if request.query_params:
        user = User.objects.filter(**request.query_params.dict())
    else:
        users = User.objects.all()

    # if there is something in items else raise error
    if users:
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)