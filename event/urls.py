from django.urls import path
from .views import (
    EventCreateAPIView, EventListAPIView, EventRetrieveAPIView, EventUpdateAPIView, EventDeleteAPIView,
    RSVPView, MyEventsView, EventAttendeesView, LikeEventView,
    CategoryListView, CategoryDetailView, TagListView, TagDetailView,
    EventStatsView, GlobalEventStatsView,
    EventMediaUploadRetrieveView,
    MyRSVPEventsView, MyLikedEventsView,
    AddReadEventCommentView, DeleteEventCommentView, SubmitEventReviewView,

)


urlpatterns = [
    # event CRUD:
    path("events/", EventListAPIView.as_view(), name="event-list"),  # List all events
    path("events/create/", EventCreateAPIView.as_view(), name="event-create"),  # Create an event
    path("events/<int:id>/", EventRetrieveAPIView.as_view(), name="event-retrieve"),  # Retrieve a specific event
    path("events/<int:id>/update/", EventUpdateAPIView.as_view(), name="event-update"),  # Update an event
    path("events/<int:id>/delete/", EventDeleteAPIView.as_view(), name="event-delete"),  # Delete an event

    # User interaction endpoints(like, RSVP)
    path('events/<int:event_id>/rsvp/', RSVPView.as_view(), name='rsvp'),
    path('my-events/', MyEventsView.as_view(), name='my-events'),
    path('events/<int:event_id>/attendees/', EventAttendeesView.as_view(), name='event-attendees'),
    path('events/<int:event_id>/like/', LikeEventView.as_view(), name='like-event'),

    # optimizing tags, categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:id>/', CategoryDetailView.as_view(), name='category-detail'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<int:id>/', TagDetailView.as_view(), name='tag-detail'),

    # statistics
    path('events/<int:event_id>/stats/', EventStatsView.as_view(), name='event-stats'),
    path('events/stats/', GlobalEventStatsView.as_view(), name='global-event-stats'),

    # managing media
    path('events/<int:event_id>/media/', EventMediaUploadRetrieveView.as_view(), name='upload-event-media'),

    # user-specific functionalities(return all RSVP-d and liked events for a specific user)
    path('my-events/rsvp/', MyRSVPEventsView.as_view(), name='my-rsvp-events'),
    path('my-events/liked/', MyLikedEventsView.as_view(), name='my-liked-events'),

    # user comment and review functionality
    path('events/<int:event_id>/comments/', AddReadEventCommentView.as_view(), name='event-comments'),
    path('events/<int:event_id>/comments/<int:cid>/', DeleteEventCommentView.as_view(), name='delete-event-comment'),
    path('events/<int:event_id>/reviews/', SubmitEventReviewView.as_view(), name='submit-event-review'),
]
