from django.test import TestCase
from django.urls import reverse


class LandingPageTests(TestCase):
    def test_pages_link_to_each_other(self):
        for name in ('home', 'about', 'contact'):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'href="%s"' % reverse('home'))
            self.assertContains(response, 'href="%s"' % reverse('about'))
            self.assertContains(response, 'href="%s"' % reverse('contact'))
            self.assertContains(response, 'href="%s"' % reverse('terms'))
            self.assertContains(response, 'href="%s"' % reverse('privacy'))
            self.assertContains(response, '/static/web/logo.jpg')
            self.assertContains(response, 'Academy CRM')

    def test_active_page(self):
        response = self.client.get(reverse('about'))
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, 'id="about"')

    def test_contact_rejects_invalid_input(self):
        response = self.client.post(reverse('contact'), {
            'name': '',
            'email': 'not-an-email',
            'message': 'short',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter your name.')
        self.assertContains(response, 'Enter an email address like name@school.edu.')
        self.assertContains(response, 'Write at least 10 characters.')

    def test_contact_accepts_a_complete_message(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Ada Lovelace',
            'email': 'ada@example.com',
            'organization': 'Analytical Academy',
            'message': 'We need a calmer way to track enrollment.',
        })
        self.assertContains(response, 'Thank you, Ada Lovelace.')

    def test_terms_and_privacy_pages(self):
        terms = self.client.get(reverse('terms'))
        privacy = self.client.get(reverse('privacy'))
        self.assertContains(terms, 'Terms and conditions')
        self.assertContains(privacy, 'Privacy policy')
        self.assertContains(terms, reverse('privacy'))
        self.assertContains(privacy, reverse('terms'))

    def test_unknown_path_uses_not_found_page(self):
        response = self.client.get('/no-such-page/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Page not found', status_code=404)
        self.assertContains(response, reverse('home'), status_code=404)
