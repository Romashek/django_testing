from notes.forms import NoteForm
from notes.tests.base_tests import BaseTestCase


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
            (self.url_add),
            (self.edit_url),
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.author_note.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
