from django.contrib import admin
from .models import Tag, Category, EventMedia, Event, EventComment, EventReview
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(EventMedia)
admin.site.register(Event)
admin.site.register(EventComment)
admin.site.register(EventReview)
