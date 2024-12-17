import hashlib

from django.core.cache import cache
from django.db.models import Q, Count
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, TagSerializer, CategorySerializer, EventMediaSerializer, EventReviewSerializer, \
    EventCommentSerializer, LikeEventSerializer
from .models import Event, Tag, Category, EventMedia, EventReview, EventComment
from .serializers import EventSerializer

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_cache_key(self, query_params):
        """
        Generate a unique cache key based on the query parameters.
        """
        query_string = '&'.join(f'{key}={value}' for key, value in query_params.items())
        return hashlib.md5(query_string.encode('utf-8')).hexdigest()

    def get_queryset(self):
        """
        Fetch and cache the queryset based on query parameters.
        """
        # Generate a unique cache key based on request parameters
        cache_key = f"events:{self.get_cache_key(self.request.GET)}"
        cached_data = cache.get(cache_key)

        if cached_data:
            print("Returning cached data")
            return cached_data

        print("Querying database")
        queryset = Event.objects.select_related('category').prefetch_related('tags')

        # Get query parameters from the request
        query = self.request.GET.get('query', None)
        date = self.request.GET.get('date', None)
        category = self.request.GET.get('category', None)
        location = self.request.GET.get('location', None)
        tags = self.request.GET.get('tags', None)

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        if date:
            queryset = queryset.filter(start_date=date)

        if category:
            queryset = queryset.filter(category__iexact=category)

        if location:
            queryset = queryset.filter(location__icontains=location)

        if tags:
            tag_names = tags.split(',')
            queryset = queryset.filter(tags__name__in=tag_names)

        cache.set(cache_key, queryset, timeout=60)

        return queryset


class EventRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticatedOrReadOnly]


# Update an event
class EventUpdateAPIView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated]


# Delete an event
class EventDeleteAPIView(generics.DestroyAPIView):
    queryset = Event.objects.all()
    lookup_field = "id"
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class RSVPView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        """
        RSVP to an Event
        """
        event = get_object_or_404(Event, id=event_id)

        if event.status == "Canceled":
            return Response(
                {"error": "You cannot RSVP to a canceled event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user in event.attendees.all():
            return Response(
                {"message": "You have already RSVP'd to this event."},
                status=status.HTTP_200_OK,
            )

        event.attendees.add(request.user)
        return Response({"message": "Successfully RSVP'd to the event!"}, status=status.HTTP_201_CREATED)

    def delete(self, request, event_id):
        """
        Withdraw RSVP from an Event
        """
        event = get_object_or_404(Event, id=event_id)

        if request.user not in event.attendees.all():
            return Response(
                {"error": "You have not RSVP'd to this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.attendees.remove(request.user)
        return Response({"message": "Your RSVP has been withdrawn."}, status=status.HTTP_200_OK)


class MyEventsView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


class EventAttendeesView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)
        return event.attendees.all()


class LikeEventView(GenericAPIView):
    serializer_class = LikeEventSerializer

    def post(self, request, event_id):
        """
        Like an Event
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = get_object_or_404(Event, id=event_id)

        if request.user in event.likes.all():
            return Response(
                {"message": "You have already liked this event."},
                status=status.HTTP_200_OK,
            )

        event.likes.add(request.user)
        event.likes_number += 1
        event.save()
        return Response({"message": "Event liked successfully!"}, status=status.HTTP_201_CREATED)

    def delete(self, request, event_id):
        """
        Unlike an Event
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = get_object_or_404(Event, id=event_id)

        if request.user not in event.likes.all():
            return Response(
                {"error": "You have not liked this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.likes.remove(request.user)
        event.likes_number -= 1
        event.save()
        return Response({"message": "Event unliked successfully."}, status=status.HTTP_200_OK)


class TagListView(generics.ListAPIView):
    """
    List all tags for events.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific tag.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'


class CategoryListView(generics.ListAPIView):
    """
    List all event categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


class EventStatsView(GenericAPIView):
    """
    Retrieve event-specific statistics (attendees, likes).
    """
    queryset = Event.objects.all()

    def get(self, request, event_id):
        # Retrieve the event
        event = get_object_or_404(Event, id=event_id)
        attendee_count = event.attendees.count()
        like_count = event.likes.count()
        stats = {
            "event_id": event.id,
            "event_title": event.title,
            "rsvp_count": attendee_count,
            "like_count": like_count,
        }

        return Response(stats, status=status.HTTP_200_OK)


class GlobalEventStatsView(GenericAPIView):
    """
    Get global event statistics (total attendees, total likes, etc.).
    """
    def get(self, request):
        # Total number of events
        total_events = Event.objects.count()
        total_attendees = Event.objects.aggregate(total_attendees=Count('attendees'))['total_attendees'] or 0
        total_likes = Event.objects.aggregate(total_likes=Count('likes'))['total_likes'] or 0
        stats = {
            "total_events": total_events,
            "total_attendees": total_attendees,
            "total_likes": total_likes,
        }

        return Response(stats, status=status.HTTP_200_OK)


class EventMediaUploadRetrieveView(APIView):
    """
    Upload event media (image/video).
    """
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = EventMediaSerializer

    def get(self, request, event_id):
        """
        Retrieve all media associated with a specific event.
        """
        event = get_object_or_404(Event, id=event_id)
        media_files = EventMedia.objects.filter(event=event)

        if not media_files.exists():
            return Response({"message": "No media files found for this event."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EventMediaSerializer(media_files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, event_id):
        """
        Handle uploading of event media.
        """
        event = get_object_or_404(Event, id=event_id)

        media_files = request.FILES.getlist('file')  # Multiple files
        print(request.FILES)
        if not media_files:
            return Response({"error": "No media files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        media_saved = []
        for media_file in media_files:
            try:
                media = EventMedia.objects.create(event=event, file=media_file)
                media_saved.append(media.file.url)  # Save URL or any relevant data
            except Exception as e:
                return Response({"error": f"Failed to upload {media_file.name}: {str(e)}"},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Media uploaded successfully.",
            "media_files": media_saved
        }, status=status.HTTP_201_CREATED)


class MyRSVPEventsView(APIView):
    """
    Retrieve a list of events the user has RSVPed to.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get(self, request):
        user = request.user
        # Get events the user has RSVPed to
        events = Event.objects.filter(attendees=user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)


class MyLikedEventsView(APIView):
    """
    Retrieve a list of events the user has liked.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def get(self, request):
        user = request.user
        # Get events the user has liked
        events = Event.objects.filter(likes=user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)


class AddReadEventCommentView(APIView):
    """
    Add or read a comment to an event.
    """
    serializer_class = EventCommentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        comments = EventComment.objects.filter(event=event)
        serializer = EventCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        comment = EventComment.objects.create(
            user=request.user,
            event=event,
            content=request.data.get('content')
        )
        return Response(
            {"message": "Comment added successfully."},
            status=status.HTTP_201_CREATED
        )


class DeleteEventCommentView(APIView):
    """
    Delete a comment from an event.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EventCommentSerializer

    def delete(self, request, event_id, cid):
        event = get_object_or_404(Event, id=event_id)
        comment = get_object_or_404(EventComment, id=cid, event=event)

        # Ensure the user is the author of the comment
        if comment.user != request.user:
            return Response(
                {"error": "You are not authorized to delete this comment."},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()
        return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class SubmitEventReviewView(APIView):
    """
    Submit a review for an event.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EventReviewSerializer

    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        reviews = EventReview.objects.filter(event=event)
        serializer = EventReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        review = EventReview.objects.create(
            user=request.user,
            event=event,
            rating=request.data.get('rating'),
            content=request.data.get('content')
        )
        return Response(
            {"message": "Review submitted successfully."},
            status=status.HTTP_201_CREATED
        )



