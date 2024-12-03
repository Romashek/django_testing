# news/tests/test_routes.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title='hello world', text='sup! thst only test dont panick!', slug='travel', author=cls.author)
    
    def test_pages_availability(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) 

    def test_auth_user_notes_done_add_access(self):
        self.client.login(username='testuser', password='testpassword')
        
        urls = (
            ('notes:list'),
            ('notes:success'),
            ('notes:add'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) 
        
    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):  
                with self.subTest(user=user, name=name):        
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
    
    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        
        urls = (
            ('notes:edit',(self.note.slug,)), 
            ('notes:delete',(self.note.slug,)),
            ('notes:add',None),
            ('notes:detail',(self.note.slug,)),
            ('notes:list',None),
            ('notes:success',None),
        )
        
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url) 
    
    
    