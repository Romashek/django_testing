from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from .base_tests import BaseTestCase
from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(BaseTestCase):
    """Тесты для создания заметок."""

    def test_anonymous_user_cant_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        NOTES_COUNT = Note.objects.count()
        self.client.post(self.url_add, data=self.form_data)
        new_notes_count = Note.objects.count()
        self.assertEqual(new_notes_count, NOTES_COUNT)

    def test_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()
        self.author_client.post(self.url_add, data=self.form_data)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)

    def test_cant_create_same_slug(self):
        """Проверяет, что нельзя создать заметку с дублирующимся slug."""
        existing_slug = self.note.slug
        response = self.author_client.post(reverse('notes:add'), data={
            'title': 'Second Note',
            'text': 'This is the second note.',
            'slug': existing_slug})

        self.assertFormError(
            response,
            'form',
            'slug',
            f'{self.note.slug}{WARNING}'
        )

    def test_if_not_slug(self):
        Note.objects.all().delete()
        title = 'Note'
        form_data = {
            'title': title,
            'text': 'This is the note without slug.',
            'slug': ''}
        self.author_client.post(self.url_add, data=form_data)
        note = Note.objects.get()
        expected_slug = slugify(title)
        self.assertEqual(expected_slug, note.slug)


class TestNoteEditDelete(BaseTestCase):
    """Тесты для редактирования и удаления заметок."""

    def test_author_can_delete_note(self):
        """Проверяет, что автор может удалить свою заметку."""
        NOTES_COUNT = Note.objects.count()
        self.author_note.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, NOTES_COUNT - 1)

    def test_user_cant_delete_note_of_another_user(self):
        NOTES_COUNT = Note.objects.count()
        response = self.reader_note.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, NOTES_COUNT)

    def test_author_can_edit_note(self):
        """Проверяет, что автор может редактировать свою заметку."""
        original_note = Note.objects.get(id=self.test_note.id)
        self.author_note.post(self.edit_url, data=self.form_data_for_logic)
        updated_note = Note.objects.get(id=self.test_note.id)
        self.assertNotEqual(original_note.text, updated_note.text)
        self.assertEqual(updated_note.text, self.form_data_for_logic['text'])
        self.assertEqual(updated_note.title, self.form_data_for_logic['title'])
        self.assertEqual(updated_note.slug, self.form_data_for_logic['slug'])
        self.assertEqual(updated_note.author, original_note.author)

    def test_user_cant_edit_note_of_another_user(self):
        original_note = Note.objects.get(id=self.note.id)
        response = self.reader_note.post(self.edit_url,
                                         data=self.form_data_for_logic)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, original_note.title)
        self.assertEqual(updated_note.text, original_note.text)
        self.assertEqual(updated_note.slug, original_note.slug)
        self.assertEqual(updated_note.author, original_note.author)
