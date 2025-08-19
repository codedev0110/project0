from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.conf import settings
from openai import OpenAI
import base64


class ExplainCodeView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        content = request.data.get('content', '')
        path = request.data.get('path', '')
        if not content:
            return Response({'error': 'content is required'}, status=400)

        api_key = settings.OPENAI_API_KEY
        if not api_key:
            return Response({'error': 'OpenAI API key not configured'}, status=500)

        client = OpenAI(api_key=api_key)
        prompt = (
            "Explain the following code in simple terms for a learner. Include what it does, key concepts, and how it works.\n"
            f"File: {path}\n\n" + content
        )
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a concise software mentor."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=500,
            )
            text = completion.choices[0].message.content
            return Response({'explanation': text})
        except Exception as exc:
            return Response({'error': str(exc)}, status=500)

# Create your views here.
