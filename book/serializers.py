from rest_framework import serializers 
from book.models import Image, History

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Image
        ordering = ['created_at']
        fields = '__all__'
        read_only_fields = ['created_at']


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model=History
        ordering = ['created_at']
        fields = '__all__'
        read_only_fields = ['created_at']

