from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Question, Answer, Vote
from .serializers import QuestionSerializer, AnswerSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().select_related('project', 'author')
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def answer(self, request, pk=None):
        question = self.get_object()
        serializer = AnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Answer.objects.create(
            question=question,
            author=request.user,
            body=serializer.validated_data['body']
        )
        return Response(QuestionSerializer(question).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        question = self.get_object()
        vote_type = request.data.get('vote')
        if vote_type not in ['up', 'down']:
            return Response({'error': 'vote must be up or down'}, status=400)
        Vote.objects.update_or_create(user=request.user, question=question, defaults={'vote_type': vote_type})
        question.score = Vote.objects.filter(question=question, vote_type='up').count() - Vote.objects.filter(question=question, vote_type='down').count()
        question.save(update_fields=['score'])
        return Response({'score': question.score})


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all().select_related('question', 'author')
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        answer = self.get_object()
        vote_type = request.data.get('vote')
        if vote_type not in ['up', 'down']:
            return Response({'error': 'vote must be up or down'}, status=400)
        Vote.objects.update_or_create(user=request.user, answer=answer, defaults={'vote_type': vote_type})
        answer.score = Vote.objects.filter(answer=answer, vote_type='up').count() - Vote.objects.filter(answer=answer, vote_type='down').count()
        answer.save(update_fields=['score'])
        return Response({'score': answer.score})

# Create your views here.
