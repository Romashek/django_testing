from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    """Базовый класс для тестов заметок."""
    TEXT = 'This is the note.'
    NEW_TEXT = 'thats test text'

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

        cls.author = User.objects.create(username='Автор комментария')
        cls.author_note = Client()
        cls.author_note.force_login(cls.author)
        cls.test_note = Note.objects.create(
            title='Note',
            text=cls.TEXT,
            slug='test-slug',
            author=cls.author
        )
        cls.note3 = Note.objects.create(
            title='User Note',
            text='This is a note .',
            slug='123',
            author=cls.author
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_note = Client()
        cls.reader_note.force_login(cls.reader)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.user2)
        cls.delete_url = reverse('notes:delete', args=(cls.test_note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.test_note.slug,))
        cls.url_add = reverse('notes:add')
        cls.url_home = reverse('notes:home')
        cls.url_edit = reverse('notes:edit', args=(cls.note3.slug,))
        cls.url_done = reverse('notes:success')
        cls.url_delete = reverse('notes:delete', args=(cls.note3.slug,))
        cls.url_list = reverse('notes:list')
        cls.url_detail = reverse('notes:detail', args=(cls.note3.slug,))
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
        cls.form_data = {
            'title': 'hello world',
            'text': 'thats test text',
            'slug': 'test'
        }
        cls.form_data_for_logic = {
            'title': 'hello world',
            'text': cls.NEW_TEXT,
            'slug': 'test'
        }

    def get_url(self, name, *args):
        """Утилита для получения URL по имени."""
        return reverse(name, args=args)
