from http import HTTPStatus


from .base_tests import BaseTestCase


class TestRoutes(BaseTestCase):
    """Тесты для проверки доступности маршрутов."""

    def test_pages_availability(self):
        """Проверяет доступность страниц для анонимного пользователя."""
        urls = (
            self.url_home,
            self.url_login,
            self.url_logout,
            self.url_signup,
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_user_notes_done_add_access(self):
        """Проверяет доступность страниц для авторизованного пользователя."""
        urls = (
            self.url_list,
            self.url_done,
            self.url_add,
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author_note, HTTPStatus.OK),
            (self.reader_note, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for name in (self.url_edit, self.url_delete, self.url_detail):
                with self.subTest(user=user, name=name):
                    response = user.get(name)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверяет редиректы для анонимных пользователей."""
        login_url = self.url_login

        urls = (
            (self.url_edit),
            (self.url_delete),
            (self.url_add),
            (self.url_detail),
            (self.url_list),
            (self.url_done),
        )

        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{login_url}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
