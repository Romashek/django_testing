# conftest.py
import pytest
from datetime import datetime, timedelta

# Импортируем класс клиента.
from django.test.client import Client
from django.conf import settings
from django.utils import timezone

from news.models import News, Comment


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст news',
    )
    return news

@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news = news,
        author = author,
        text='Текст commenta',
    )
    return comment

@pytest.fixture
def many_news(author):
    today = datetime.today()
    News.objects.bulk_create(
            News(title=f'Новость {index}', text='Просто текст.', date= today - timedelta(days=index))
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        )

@pytest.fixture
def many_comments(author, news):
    now = timezone.now()
    for index in range(10):
            comment = Comment.objects.create(
                news=news, author=author, text=f'Tекст {index}',
            )
            comment.created = now + timedelta(days=index)
            comment.save()      

@pytest.fixture
def form_data():
    return {'text': settings.COMMENT_TEXT,} 