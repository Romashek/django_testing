import pytest
from django.conf import settings

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': settings.COMMENT_TEXT}

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(news, get_detail_url, client):
    """Проверяет, что анонимный пользователь не может создать комментарий."""
    comments_count_start = Comment.objects.count()
    url = get_detail_url(news)
    client.post(url, data=FORM_DATA)

    comments_count_finish = Comment.objects.count()
    assert comments_count_finish == comments_count_start


def test_user_can_create_comment(not_author_client, news, get_detail_url):
    """Проверяет, что авторизованный пользователь может создать комментарий."""
    Comment.objects.all().delete()
    url = get_detail_url(news)
    response = not_author_client.post(url, data=FORM_DATA)

    assert response['Location'] == f'{url}#comments'

    comments_count = Comment.objects.count()
    assert comments_count == 1

    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.author == not_author_client.user
    assert comment.news == news


def test_user_cant_use_bad_words(not_author_client, news, get_detail_url):
    comments_count_start = Comment.objects.count()
    url = get_detail_url(news)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

    response = not_author_client.post(url, data=bad_words_data)
    comments_count_finish = Comment.objects.count()
    form = response.context['form']

    assert comments_count_start == comments_count_finish
    assert 'text' in form.errors
    assert WARNING in form.errors['text']


def test_author_can_delete_comment(author_client, news, comment,
                                   get_delete_url, get_detail_url):
    """Проверяет, что автор комментария может его удалить."""
    delete_url = get_delete_url(news)
    response = author_client.delete(delete_url)
    assert response['Location'] == f'{get_detail_url(news)}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        not_author_client, news, comment, get_delete_url):
    delete_url = get_delete_url(news)
    not_author_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, comment, news, get_edit_url, get_detail_url):
    edit_url = get_edit_url(news)

    response = author_client.post(edit_url, data=FORM_DATA)
    assert response['Location'] == f'{get_detail_url(news)}#comments'

    updated_comment = Comment.objects.get(id=comment.id)

    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.author == author_client.user
    assert updated_comment.news == news


def test_user_cant_edit_comment_of_another_user(
        not_author_client, get_edit_url, comment, news, author_client):
    edit_url = get_edit_url(news)

    not_author_client.post(edit_url, data=FORM_DATA)
    updated_comment = Comment.objects.get(id=comment.id)

    assert comment.text == updated_comment.text
    assert updated_comment.author == author_client.user
    assert updated_comment.news == news
