from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class GameSerializer(serializers.ModelSerializer):
    sell_price = serializers.ReadOnlyField()

    class Meta:
        model = Game
        fields = [
            'id',
            'title',
            'description',
            'genre',
            'release_year',
            'rating',
            'price',
            'discount',
            'sell_price',
        ]

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = [
            'username',
            'nickname',
            'bio',
            'status',
        ]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username')
    receiver = serializers.CharField(source='receiver.username')

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'text',
            'timestamp'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'game',
            'text',
            'rating',
        ]