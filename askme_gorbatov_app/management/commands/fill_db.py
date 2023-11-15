from django.core.management import BaseCommand
from django.contrib.auth.models import User
from askme_gorbatov_app.models import Profile, Question, Tag, QuestionLike, CommentLike, Comment
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = "Fills database with fake data"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int)

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        profiles = [
            Profile(
                user=User.objects.create(username=fake.unique.user_name(), email=fake.email())
            ) for _ in range(ratio)
        ]

        Profile.manager.bulk_create(profiles)
        profiles = Profile.manager.all()

        tags = [
            Tag(
                name=f"Tag №{i}"
            ) for i in range(ratio)
        ]
        Tag.manager.bulk_create(tags)

        questions = []
        for _ in range(ratio * 10):
            author = random.choice(profiles)
            create_date = fake.date_time()
            title = fake.sentence(nb_words=5)
            content = fake.paragraph()
            question = Question.manager.create(author=author, create_date=create_date, title=title, content=content)
            question.tags.set(random.sample(tags, random.randint(1, 3)))

        Question.manager.bulk_create(questions)
        questions = Question.manager.all()
        comments = [
            Comment(
                author=random.choice(profiles),
                question=random.choice(questions),
                create_date=fake.date_time(),
                content=fake.paragraph(),
                is_correct=fake.pybool()
            ) for _ in range(ratio * 100)
        ]

        Comment.manager.bulk_create(comments)
        comments = Comment.manager.all()
        questions = Question.manager.all()
        existing_likes = set()
        desired_likes = ratio * 100
        likes_to_create = []
        while len(likes_to_create) < desired_likes:
            question = random.choice(questions)
            profile = random.choice(profiles)
            if (profile.id, question.id) not in existing_likes:
                like = QuestionLike(author=profile, question=question)
                likes_to_create.append(like)
                existing_likes.add((profile.id, question.id))
        QuestionLike.objects.bulk_create(likes_to_create)

        existing_likes = set()
        desired_likes = ratio * 100
        likes_created = []
        while len(likes_to_create) < desired_likes:
            comment = random.choice(comments)
            profile = random.choice(profiles)
            if (profile.id, comment.id) not in existing_likes:
                like = CommentLike(author=profile, comment=comment)
                likes_created.append(like)
                existing_likes.add((profile.id, comment.id))
        CommentLike.objects.bulk_create(likes_created)