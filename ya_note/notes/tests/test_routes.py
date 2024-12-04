from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .base_tests import BaseTestCase
from notes.models import Note

User = get_user_model()


class TestRoutes(BaseTestCase):
    """Тесты для проверки доступности маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для всех тестов."""
        super().setUpTestData()
        cls.author = User.objects.create_user(username='Автор',
                                              password='password')
        cls.reader = User.objects.create_user(username='Читатель простой',
                                              password='password')
        cls.note3 = Note.objects.create(
            title='User Note',
            text='This is a note .',
            slug='123',
            author=cls.author
        )
        cls.url_add = 'notes:add'
        cls.url_home = 'notes:home'
        cls.url_edit = 'notes:edit'
        cls.url_done = 'notes:success'
        cls.url_delete = 'notes:delete'
        cls.url_list = 'notes:list'
        cls.url_detail = 'notes:detail'

    def test_pages_availability(self):
        """Проверяет доступность страниц для анонимного пользователя."""
        urls = (
            self.url_home,
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
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
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (self.url_edit, self.url_delete, self.url_detail):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note3.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверяет редиректы для анонимных пользователей."""
        login_url = reverse('users:login')

        urls = (
            (self.url_edit, (self.note.slug,)),
            (self.url_delete, (self.note.slug,)),
            (self.url_add, None),
            (self.url_detail, (self.note.slug,)),
            (self.url_list, None),
            (self.url_done, None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
