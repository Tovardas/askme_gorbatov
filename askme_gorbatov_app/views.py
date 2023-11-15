from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)
from askme_gorbatov_app.models import Question, Tag, Comment, Profile
from django.db.models import Count

def paginate(objects, request, per_page=5):
    page = request.GET.get('page', 1)
    paginator = Paginator(objects, per_page)
    default_page = 1
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(default_page)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)
    return items_page


def index(request):
    questions = Question.manager.get_new_questions()
    items_page = paginate(questions, request, 5)
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'index.html', {'questions': items_page, 'pages': items_page, 'tags': top_tags, 'users': top_users})


def question(request, question_id):
    try:
        item = Question.manager.get_question_by_id(question_id)
    except:
        return HttpResponseBadRequest()
    comments = Comment.manager.get_comments_ordered_by_likes(question_id)
    items_page = paginate(comments, request, 30)
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'question.html', {'question': item, 'comments': items_page,
                                             'pages': items_page, 'question_id': question_id, 'tags': top_tags,'users': top_users})


def ask(request):
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'ask.html', {'tags': top_tags,'users': top_users})


def signup(request):
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'signup.html', {'tags': top_tags,'users': top_users})


def login(request):
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'login.html', {'tags': top_tags,'users': top_users})


def hot(request):
    items_page = paginate(Question.manager.get_top_questions(), request)
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'hot.html', {'questions': items_page, 'pages': items_page, 'tags': top_tags,'users': top_users})


def settings(request):
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'settings.html', {'tags': top_tags,'users': top_users})


def tag(request, tag_name):
    tag_item = Tag.manager.get_questions_by_tag(tag_name)
    items_page = paginate(tag_item.order_by('-create_date'), request)
    top_tags = Tag.manager.top_of_tags(10)
    top_users = Profile.manager.get_top_users(10)
    return render(request, 'tag.html', {'tag': tag_name, 'questions': items_page, 'pages': items_page, 'tags': top_tags,'users': top_users})