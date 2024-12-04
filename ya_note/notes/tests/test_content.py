from django.urls import reverse

from .base_tests import BaseTestCase
from notes.forms import NoteForm


class TestContent(BaseTestCase):
    """Тесты для проверки контента заметок."""

    def test_notes_list_page_includes_note_in_context(self):
        response = self.author_client.get(self.url_list)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_list_excludes_other_users_notes(self):
        response = self.author_client.get(self.url_list)
        self.assertIn(self.note, response.context['object_list'])
        self.assertNotIn(self.note2, response.context['object_list'])

    def test_form_in_add_edit(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
