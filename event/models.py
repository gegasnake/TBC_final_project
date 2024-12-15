from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from user.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    is_online = models.BooleanField(default=False)
    link = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=[
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('canceled', 'Canceled'),
    ], default='scheduled')
    attendees = models.ManyToManyField(CustomUser, blank=True, related_name='attendees')
    capacity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    likes_number = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(CustomUser, blank=True, related_name='liked_events')

    def __str__(self):
        return self.title


class EventMedia(models.Model):
    event = models.ForeignKey(Event, related_name='media', on_delete=models.CASCADE)
    file = models.FileField(upload_to='event_media/')
    media_type = models.CharField(max_length=50, choices=[('image', 'Image'), ('video', 'Video')], default='image')
    created_at = models.DateTimeField(auto_now_add=True)


class EventComment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.event.title}"


class EventReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Rating between 1 and 5
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review by {self.user.username} on {self.event.title}"

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError('Rating must be between 1 and 5.')


class LikeEvent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure each user can like an event only once
        unique_together = ('user', 'event')  # Combination of user and event must be unique

    def __str__(self):
        return f"{self.user.username} liked {self.event.title}"


