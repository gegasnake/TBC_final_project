from rest_framework import serializers

from user.models import CustomUser
from .models import Event, Category, Tag, EventMedia, EventComment, EventReview, LikeEvent


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class EventMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMedia
        fields = ['id', 'file', 'media_type', 'created_at']


class EventCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    event = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventComment
        fields = ['id', 'user', 'event', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'event', 'created_at']


class EventReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    event = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventReview
        fields = ['id', 'user', 'event', 'rating', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'event', 'created_at']


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    media = EventMediaSerializer(many=True, read_only=True)
    reviews = EventReviewSerializer(many=True, read_only=True)
    comments = EventCommentSerializer(many=True, read_only=True)
    attendees = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date', 'location', 'status', 'category', 'tags',
            'likes_number', 'attendees', 'media', 'reviews', 'comments'
        ]
        read_only_fields = ['attendees', 'likes_number', 'media', 'reviews', 'comments', 'organizer']

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        tags_data = validated_data.pop('tags')
        category, _ = Category.objects.get_or_create(**category_data)
        tags = []
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            tags.append(tag)
        request = self.context.get('request')
        organizer = request.user if request else None
        if not organizer:
            raise serializers.ValidationError({'organizer': 'Organizer is required.'})
        event = Event.objects.create(category=category, organizer=organizer, **validated_data)
        event.tags.set(tags)

        return event

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        if category_data:
            category, _ = Category.objects.get_or_create(**category_data)
            instance.category = category

        tags_data = validated_data.pop('tags', None)
        if tags_data:
            tags = []
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(**tag_data)
                tags.append(tag)
            instance.tags.set(tags)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class EventMediaUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMedia
        fields = ['id', 'file', 'event']


class LikeEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = LikeEvent
        fields = ['created_at']
        read_only_fields = ['created_at']  # Don't allow manual setting of 'created_at'

    def create(self, validated_data):
        # Create and return the LikeEvent instance
        return LikeEvent.objects.create(**validated_data)



