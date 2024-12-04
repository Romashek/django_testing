from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для тестов заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для всех тестов."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        cls.user2 = User.objects.create_user(username='user2',
                                             password='password2')
        cls.note = Note.objects.create(
            title='Test Note',
            text='This is a test note.',
            slug='travel',
            author=cls.user
        )
        cls.note2 = Note.objects.create(
            title='User 2 Note',
            text='This is a note for user 2.',
            slug='test2',
            author=cls.user2
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.user2)
        cls.url_list = reverse('notes:list')
        cls.NOTES_COUNT = Note.objects.count()

    def get_url(self, name, *args):
        """Утилита для получения URL по имени."""
        return reverse(name, args=args)
