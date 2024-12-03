import pytest
from django.urls import reverse
from django.conf import settings
from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def get_detail_url(news):
    """Возвращает URL страницы деталей новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.mark.django_db
def get_delete_url(news):
    """Возвращает URL для удаления новости."""
    return reverse('news:delete', args=(news.id,))


@pytest.mark.django_db
def get_edit_url(news):
    """Возвращает URL для редактирования новости."""
    return reverse('news:edit', args=(news.id,))


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, client, form_data):
    """Проверяет, что анонимный пользователь не может создать комментарий."""
    url = get_detail_url(news)
    client.post(url, data=form_data)

    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(not_author_client, form_data, news):
    """Проверяет, что авторизованный пользователь может создать комментарий."""
    url = get_detail_url(news)
    response = not_author_client.post(url, data=form_data)

    assert response['Location'] == f'{url}#comments'

    comments_count = Comment.objects.count()
    assert comments_count == 1

    comment = Comment.objects.get()
    assert comment.text == settings.COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_use_bad_words(not_author_client, news):
    url = get_detail_url(news)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

    response = not_author_client.post(url, data=bad_words_data)

    form = response.context['form']

    assert 'text' in form.errors
    assert WARNING in form.errors['text']

    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    """Проверяет, что автор комментария может его удалить."""
    delete_url = get_delete_url(news)
    response = author_client.delete(delete_url)
    assert response['Location'] == f'{get_detail_url(news)}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        not_author_client, news, comment):
    delete_url = get_delete_url(news)
    not_author_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client, comment, form_data, news):
    edit_url = get_edit_url(news)

    response = author_client.post(edit_url, data=form_data)
    assert response['Location'] == f'{get_detail_url(news)}#comments'

    comment.refresh_from_db()

    assert comment.text == settings.COMMENT_TEXT


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment, form_data, news):
    edit_url = get_edit_url(news)

    not_author_client.post(edit_url, data=form_data)
    comment.refresh_from_db()

    assert comment.text == 'Текст commenta'
