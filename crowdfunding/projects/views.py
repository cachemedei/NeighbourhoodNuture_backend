from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404

from .permissions import IsOwnerOrReadOnly, IsSupporterOrReadOnly
from .models import Project, Pledge
from .serializers import ProjectSerializer, PledgeSerializer, ProjectDetailSerializer, PledgeDetailSerializer

# all projects
class ProjectList(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user) ##
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )

# specific project
class ProjectDetail(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            project = Project.objects.get(pk=pk)
            self.check_object_permissions(self.request, project)
            return project
        except Project.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)
    
    def put(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectDetailSerializer(
            instance=project,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # delete project
    def delete(self, request, pk):
        project = self.get_object(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# all pledges
class PledgeList(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        pledges = Pledge.objects.all()
        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PledgeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(supporter=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class PledgeDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSupporterOrReadOnly]

    def get_object(self, pk):
        try:
            pledge = Pledge.objects.get(pk=pk)
            self.check_object_permissions(self.request, pledge)
            return pledge
        except Pledge.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        pledge = self.get_object(pk)
        serializer = PledgeDetailSerializer(pledge)
        return Response(serializer.data)
    
    def put(self, request, pk):
        pledge = self.get_object(pk)
        serializer = PledgeDetailSerializer(
            instance=pledge,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # delete pledge
    def delete(self, request, pk):
        pledge = self.get_object(pk)
        pledge.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

# projects by specific owner
class UserProjectsView(APIView):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, id):
        projects = Project.objects.filter(owner=id)
        if not projects:
            return Response(
                {'detail': 'no projects found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)