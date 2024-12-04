from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from pytils.translit import slugify

from .base_tests import BaseTestCase
from notes.models import Note

User = get_user_model()


class TestNoteCreation(BaseTestCase):
    """Тесты для создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для всех тестов."""
        super().setUpTestData()
        cls.url_add = reverse('notes:add')
        cls.form_data = {
            'title': 'hello world',
            'text': 'thats test text',
            'slug': 'test'
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        self.client.post(self.url_add, data=self.form_data)
        new_notes_count = Note.objects.count()
        self.assertEqual(new_notes_count, self.NOTES_COUNT)

    def test_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        self.author_client.post(self.url_add, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTES_COUNT+1)
        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])

    def test_cant_create_same_slug(self):
        """Проверяет, что нельзя создать заметку с дублирующимся slug."""
        response = self.author_client.post(reverse('notes:add'), data={
        'title': 'Second Note',
        'text': 'This is the second note.',
        'slug': 'travel'})

        self.assertFormError(response, 'form', 'slug', 
                         f'{self.note.slug} - такой slug уже существует, придумайте уникальное значение!')

    def test_if_not_slug(self):
        title = 'Note'
        form_data = {
        'title': title,
        'text': 'This is the note without slug.',
        'slug': ''}
        response = self.author_client.post(self.url_add, data=form_data)
        note = Note.objects.get(title=title)
        expected_slug = slugify(title)
        self.assertEqual(expected_slug, note.slug)


class TestNoteEditDelete(BaseTestCase):
    """Тесты для редактирования и удаления заметок."""

    TEXT = 'This is the note.'
    NEW_TEXT = 'thats test text'

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные для всех тестов."""
        super().setUpTestData()
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
        self.assertEqual(notes_count, self.NOTES_COUNT)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTES_COUNT+1)

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        original_note = Note.objects.get(id=self.note.id)
        self.author_client.post(self.edit_url, data=self.form_data)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertNotEqual(original_note.text, updated_note.text)
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, original_note.author)

    def test_user_cant_edit_note_of_another_user(self):
        original_note = Note.objects.get(id=self.note.id)
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, original_note.title)
        self.assertEqual(updated_note.text, original_note.text)
        self.assertEqual(updated_note.slug, original_note.slug)
        self.assertEqual(updated_note.author, original_note.author)
