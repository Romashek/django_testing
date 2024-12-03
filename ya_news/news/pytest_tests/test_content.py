import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm


@pytest.mark.django_db
def get_home_url():
    return reverse('news:home')


@pytest.mark.django_db
def get_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.mark.django_db
def get_news_from_response(response):
    return response.context['news']


@pytest.mark.django_db
def test_count_page_on_home(many_news, client):
    url = get_home_url()
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()

    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(many_news, client):
    url = get_home_url()
    response = client.get(url)
    object_list = response.context['object_list']

    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comment_order(client, news):
    url = get_detail_url(news)
    response = client.get(url)

    assert 'news' in response.context

    news_instance = get_news_from_response(response)

    all_comments = news_instance.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]

    sorted_timestamps = sorted(all_timestamps)

    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    url = get_detail_url(news)
    response = client.get(url)

    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(not_author_client, news):
    url = get_detail_url(news)
    response = not_author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
