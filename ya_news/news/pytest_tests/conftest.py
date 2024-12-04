from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Создает пользователя-автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создает пользователя, который не является автором."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Создает клиент для авторизованного пользователя."""
    client = Client()
    client.force_login(author)
    client.user = author
    return client


@pytest.fixture
def not_author_client(not_author):
    """Создает клиент для неавторизованного пользователя."""
    client = Client()
    client.force_login(not_author)
    client.user = not_author
    return client


@pytest.fixture
def news(author):
    """Создает новость, связанную с автором."""
    return News.objects.create(
        title='Заголовок',
        text='Текст news'
    )


@pytest.fixture
def comment(author, news):
    """Создает комментарий к новости от автора."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст commenta',
    )


@pytest.fixture
def many_news(author):
    """Создает несколько новостей для тестирования."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def many_comments(author, news):
    """Создает несколько комментариев к новости от автора."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def get_detail_url():
    def _get_detail_url(news):
        return reverse('news:detail', args=(news.id,))
    return _get_detail_url


@pytest.fixture
def get_delete_url():
    def _get_delete_url(news):
        return reverse('news:delete', args=(news.id,))
    return _get_delete_url


@pytest.fixture
def get_edit_url():
    def _get_edit_url(news):
        return reverse('news:edit', args=(news.id,))
    return _get_edit_url


@pytest.fixture
def get_home_url():
    def _get_home_url():
        return reverse('news:home')
    return _get_home_url
