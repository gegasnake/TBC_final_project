from rest_framework import status
from rest_framework.generics import CreateAPIView, get_object_or_404, RetrieveUpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import CustomUserSerializer, UserSerializer, UserProfileSerializer, FollowerFollowingSerializer


class RegisterView(CreateAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = UserSerializer

    def post(self, request, user_id):
        """
        Follow or unfollow a user.
        """
        target_user = get_object_or_404(CustomUser, id=user_id)
        current_user = request.user

        if target_user == current_user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if current_user in target_user.followers.all():
            target_user.followers.remove(current_user)
            action = "unfollowed"
        else:
            target_user.followers.add(current_user)
            action = "followed"

        return Response({"message": f"You have {action} {target_user.username}."}, status=status.HTTP_200_OK)


class UserProfileView(RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the authenticated user's instance
        return self.request.user


class FollowersListView(ListAPIView):
    serializer_class = FollowerFollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all users who follow the authenticated user
        return self.request.user.followers.all()


class FollowingsListView(ListAPIView):
    serializer_class = FollowerFollowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all users the authenticated user is following
        return self.request.user.following.all()
