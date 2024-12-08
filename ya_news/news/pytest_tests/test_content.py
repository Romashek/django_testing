import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def get_news_from_response(response):
    return response.context['news']


def test_count_page_on_home(many_news, get_home_url, client):
    url = get_home_url
    response = client.get(url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(many_news, client, get_home_url):
    url = get_home_url
    response = client.get(url)

    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


def test_comment_order(client, news, get_detail_url):
    url = get_detail_url(news)
    response = client.get(url)

    assert 'news' in response.context

    news_instance = get_news_from_response(response)

    all_comments = news_instance.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]

    sorted_timestamps = sorted(all_timestamps)

    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news, get_detail_url):
    url = get_detail_url(news)
    response = client.get(url)

    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, get_detail_url, news):
    url = get_detail_url(news)
    response = not_author_client.get(url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
