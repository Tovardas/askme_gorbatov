from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count


# Create your models here.


class ProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            popular_question_count=Count('questions'),
            popular_answer_count=Count('comments')
        )

    def get_top_users(self, n):
        qs = self.get_queryset().order_by('-popular_question_count', '-popular_answer_count')[:n]
        return qs


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='static/img', null=True, blank=True)
    manager = ProfileManager()

    def __str__(self):
        return f"{self.user.username} profile"


class QuestionManager(models.Manager):

    def get_new_questions(self):
        return Question.manager.all().order_by('-create_date')

    def get_top_questions(self):
        return self.get_queryset().annotate(num_likes=Count('question_likes')) \
            .order_by('-num_likes') \
            .prefetch_related('question_likes')

    def get_question_by_id(self, id):
        return Question.manager.get(pk=id)


class Question(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='questions')
    create_date = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=64)
    content = models.TextField()
    tags = models.ManyToManyField('Tag', related_name='questions')
    manager = QuestionManager()

    def __str__(self):
        return f"Question {self.title}"

    def get_answers_count(self):
        return self.comments.count()

    def get_likes_count(self):
        return self.question_likes.count()


class CommentManager(models.Manager):
    def get_comments_ordered_by_likes(self, question_id):
        comments = self.filter(question=question_id).annotate(num_likes=Count('comment_likes')).order_by('-num_likes',
                                                                                                         '-create_date')
        return comments


class Comment(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='comments')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='comments')
    create_date = models.DateTimeField(auto_now=True)
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    manager = CommentManager()

    def __str__(self):
        return f"Comment {self.content}"

    def get_likes_count(self):
        return self.comment_likes.count()


class TagManager(models.Manager):
    def top_of_tags(self, n):
        return self.get_queryset().annotate(num_questions=Count('questions')).order_by('-num_questions')[:n]

    def get_questions_by_tag(self, tag_name):
        tag = Tag.manager.get(name=tag_name)
        return tag.questions.all()


class Tag(models.Model):
    name = models.CharField(max_length=25, unique=True)
    manager = TagManager()

    def __str__(self):
        return f"{self.name}"


class QuestionLikeManager(models.Manager):
    def like_question(self, user, question):
        if self.filter(author=user, question=question).exists():
            self.filter(author=user, question=question).delete()
        else:
            self.create(author=user, question=question)

class QuestionLike(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='question_likes')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='question_likes')


class CommentLikeManager(models.Manager):
    def like_comment(self, user, comment):
        if self.filter(author=user, comment=comment).exists():
            self.filter(author=user, comment=comment).delete()
        else:
            self.create(author=user, comment=comment)


class CommentLike(models.Model):
    author = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='comment_likes')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='comment_likes')