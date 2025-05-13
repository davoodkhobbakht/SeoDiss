import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import WebToken  # Assume this model stores WP token and site_url per user
from .serializers import ProductContentSerializer, QuestionReplySerializer
from .utils import generate_seo_article, generate_question_reply  # Your GPT-powered logic

class PostProductArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductContentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_name = serializer.validated_data['product_name']
        keywords = serializer.validated_data.get('keywords', [])
        internal_links = serializer.validated_data.get('internal_links', [])
        user = request.user

        try:
            web_token = WebToken.objects.get(user=user)
        except WebToken.DoesNotExist:
            return Response({'error': 'No credentials stored.'}, status=400)

        article_data = generate_seo_article(product_name, keywords, internal_links)

        wp_post_payload = {
            'title': article_data['title'],
            'content': article_data['content'],
            'status': 'publish',
            'meta': article_data['meta'],
            'seo': article_data['seo']
        }

        response = requests.post(
            f"{web_token.site_url}/wp-json/wp/v2/posts",
            headers={'Authorization': f"Bearer {web_token.token}"},
            json=wp_post_payload
        )

        if response.status_code in [200, 201]:
            return Response({'message': 'Article posted successfully.'})
        else:
            return Response({'error': 'Failed to post article.', 'wp_error': response.json()}, status=500)


class PostProductQAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuestionReplySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_name = serializer.validated_data['product_name']
        question_count = serializer.validated_data.get('question_count', 3)
        user = request.user

        try:
            web_token = WebToken.objects.get(user=user)
        except WebToken.DoesNotExist:
            return Response({'error': 'No credentials stored.'}, status=400)

        qa_list = generate_question_reply(product_name, question_count)

        created = []

        for qa in qa_list:
            payload = {
                'title': qa['question'],
                'content': qa['answer'],
                'status': 'publish',
                'categories': [web_token.qa_category_id]  # Optional: place in a FAQ category
            }
            response = requests.post(
                f"{web_token.site_url}/wp-json/wp/v2/posts",
                headers={'Authorization': f"Bearer {web_token.token}"},
                json=payload
            )
            if response.status_code in [200, 201]:
                created.append(qa['question'])

        return Response({'message': f'{len(created)} Q&As posted.', 'questions': created})
