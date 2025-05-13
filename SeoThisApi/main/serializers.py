from rest_framework import serializers

class ProductContentSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    keywords = serializers.ListField(child=serializers.CharField(), required=False)
    internal_links = serializers.ListField(child=serializers.CharField(), required=False)

class QuestionReplySerializer(serializers.Serializer):
    product_name = serializers.CharField()
    question_count = serializers.IntegerField(default=3)
