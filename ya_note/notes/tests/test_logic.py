from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify
from django.core.exceptions import ValidationError

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты для создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для всех тестов."""
        cls.user = User.objects.create_user(username='testuser',
                                            password='testpassword')
        cls.form_data = {
            'title': 'hello world',
            'text': 'thats test text',
            'slug': 'test'
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        self.client.post(reverse('notes:add'), data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        self.client.login(username='testuser', password='testpassword')
        self.client.post(reverse('notes:add'), data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_cant_create_same_slug(self):
        """Проверяет, что нельзя создать заметку с дублирующимся slug."""
        Note.objects.create(
            title='First Note',
            text='This is the first note.',
            author=self.user,
            slug='unique-slug'
        )
        duplicate_note = Note(
            title='Second Note',
            text='This is the second note.',
            author=self.user,
            slug='unique-slug'
        )

        with self.assertRaises(ValidationError):
            duplicate_note.full_clean()

    def test_if_not_slug(self):
        title = 'Note'
        note = Note.objects.create(title=title,
                                   text='This is the note without slug.',
                                   author=self.user)
        expected_slug = slugify(title)
        self.assertEqual(expected_slug, note.slug)


class TestNoteEditDelete(TestCase):
    """Тесты для редактирования и удаления заметок."""

    TEXT = 'This is the note.'
    NEW_TEXT = 'thats test text'

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для всех тестов."""
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Note',
            text=cls.TEXT,
            slug='test-slug',
            author=cls.author
        )
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.form_data = {
            'title': 'hello world',
            'text': cls.NEW_TEXT,
            'slug': 'test'
        }

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        self.author_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT)
