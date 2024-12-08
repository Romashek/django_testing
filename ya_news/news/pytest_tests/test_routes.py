from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture',
    (pytest.lazy_fixture('get_home_url'), pytest.lazy_fixture('login_url'),
     pytest.lazy_fixture('logout_url'), pytest.lazy_fixture('signup_url')),
)
def test_pages_availability_for_anonymous_user(client, url_fixture):
    response = client.get(url_fixture)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_page_accessible_to_anonymous_user(client,
                                                       get_detail_url, news):
    url = get_detail_url(news)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture',
    (pytest.lazy_fixture('get_delete_url'),
     pytest.lazy_fixture('get_edit_url')),
)
def test_delete_edit_to_author(comment, author_client, url_fixture):
    url = url_fixture(comment)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture, parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('get_delete_url'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('get_edit_url'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK)
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, url_fixture, comment, expected_status
):
    url = url_fixture(comment)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture',
    (
        pytest.lazy_fixture('get_edit_url'),
        pytest.lazy_fixture('get_delete_url'),
    ),
)
def test_redirects(client, url_fixture, comment):
    login_url = reverse('users:login')
    url = url_fixture(comment)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
