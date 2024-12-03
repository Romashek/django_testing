# news/tests/test_content.py
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone

from notes.models import Note


User = get_user_model()

class TestContent(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.user2 = User.objects.create_user(username='user2', password='password2')
        cls.note = Note.objects.create(title='Test Note', text='This is a test note.', slug='travel', author=cls.user)
        cls.note2 = Note.objects.create(title='User 2 Note', text='This is a note for user 2.', slug='test2', author=cls.user2)

    def test_notes_list_page_includes_note_in_context(self):
            self.client.login(username='testuser', password='testpassword')
            
            url = reverse('notes:list')
            response = self.client.get(url)

            self.assertIn('object_list', response.context)
            self.assertIn(self.note, response.context['object_list'])
            
    def test_notes_list_excludes_other_users_notes(self):
        self.client.login(username='testuser', password='testpassword')
        
        url = reverse('notes:list')
        response = self.client.get(url)
        
        self.assertIn(self.note, response.context['object_list'])
        self.assertNotIn(self.note2, response.context['object_list'])
    
    def test_form_in_add_edit(self):
        self.client.login(username='testuser', password='testpassword')
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context) 