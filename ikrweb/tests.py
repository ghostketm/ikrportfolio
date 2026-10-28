"""
ikrweb/tests.py

Backend tests for the IKR portfolio application.
Run with: python manage.py test ikrweb
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import About, Certification, Contact, Education, Experience, Project, Skill


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class ProjectModelTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            title='Test Project',
            slug='test-project',
            description='A test project.',
            technologies='Django, Python, PostgreSQL',
            featured=True,
            is_published=True,
        )

    def test_technologies_list(self):
        techs = self.project.get_technologies_list()
        self.assertEqual(techs, ['Django', 'Python', 'PostgreSQL'])

    def test_get_absolute_url(self):
        url = self.project.get_absolute_url()
        self.assertIn(str(self.project.pk), url)

    def test_unpublished_not_in_list(self):
        self.project.is_published = False
        self.project.save()
        self.assertEqual(Project.objects.filter(is_published=True).count(), 0)


class SkillModelTests(TestCase):

    def test_level_percentage(self):
        skill = Skill(name='Python', level='expert', category='Engineering')
        self.assertEqual(skill.level_percentage, 100)
        skill.level = 'advanced'
        self.assertEqual(skill.level_percentage, 75)
        skill.level = 'intermediate'
        self.assertEqual(skill.level_percentage, 50)
        skill.level = 'beginner'
        self.assertEqual(skill.level_percentage, 25)


class ExperienceModelTests(TestCase):

    def test_duration_label_current(self):
        exp = Experience(
            job_title='Developer',
            company='Acme',
            start_date=timezone.datetime(2024, 1, 1).date(),
            is_current=True,
        )
        self.assertIn('Present', exp.duration_label)

    def test_duration_label_past(self):
        exp = Experience(
            job_title='Intern',
            company='Acme',
            start_date=timezone.datetime(2023, 7, 1).date(),
            end_date=timezone.datetime(2023, 9, 30).date(),
            is_current=False,
        )
        self.assertIn('Sep 2023', exp.duration_label)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class HomeViewTests(TestCase):

    def test_home_ok(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'ikrweb/home.html')

    def test_home_context_keys(self):
        resp = self.client.get(reverse('home'))
        for key in ('about', 'featured_projects', 'skills', 'project_count', 'skill_count'):
            self.assertIn(key, resp.context)

    def test_home_featured_projects_published_only(self):
        Project.objects.create(
            title='Hidden', slug='hidden', description='...',
            technologies='Django', featured=True, is_published=False,
        )
        Project.objects.create(
            title='Visible', slug='visible', description='...',
            technologies='Django', featured=True, is_published=True,
        )
        resp = self.client.get(reverse('home'))
        self.assertEqual(len(resp.context['featured_projects']), 1)
        self.assertEqual(resp.context['featured_projects'][0].title, 'Visible')


class ProjectViewTests(TestCase):

    def setUp(self):
        self.pub = Project.objects.create(
            title='Published', slug='published', description='...',
            technologies='Django', is_published=True,
        )
        self.hidden = Project.objects.create(
            title='Hidden', slug='hidden-project', description='...',
            technologies='Django', is_published=False,
        )

    def test_project_list_published_only(self):
        resp = self.client.get(reverse('project_list'))
        self.assertEqual(resp.status_code, 200)
        projects = list(resp.context['projects'])
        self.assertIn(self.pub, projects)
        self.assertNotIn(self.hidden, projects)

    def test_project_detail_published(self):
        resp = self.client.get(reverse('project_detail', args=[self.pub.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_project_detail_unpublished_404(self):
        resp = self.client.get(reverse('project_detail', args=[self.hidden.pk]))
        self.assertEqual(resp.status_code, 404)


class ContactFormTests(TestCase):

    def test_get_contact_page(self):
        resp = self.client.get(reverse('contact'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

    def test_valid_submission_saves(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Hello',
            'message': 'This is a test message for the portfolio.',
        }
        resp = self.client.post(reverse('contact'), data)
        self.assertRedirects(resp, reverse('contact'))
        self.assertEqual(Contact.objects.count(), 1)

    def test_short_message_rejected(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Hi',
            'message': 'Hi',
        }
        resp = self.client.post(reverse('contact'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp.context['form'], 'message',
                             'Please provide a more detailed message (at least 10 characters).')
        self.assertEqual(Contact.objects.count(), 0)

    def test_invalid_email_rejected(self):
        data = {
            'name': 'Test User',
            'email': 'not-an-email',
            'subject': 'Hello',
            'message': 'A sufficiently long test message for validation.',
        }
        resp = self.client.post(reverse('contact'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context['form'].is_valid())


class EducationViewTests(TestCase):

    def test_education_page_ok(self):
        resp = self.client.get(reverse('education'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('education_list', resp.context)
        self.assertIn('certifications', resp.context)


class BusinessCardViewTests(TestCase):

    def test_business_card_ok(self):
        resp = self.client.get(reverse('bussiness_card'))
        self.assertEqual(resp.status_code, 200)


class TippingViewTests(TestCase):

    def test_tipping_page_ok(self):
        resp = self.client.get(reverse('tipping'))
        self.assertEqual(resp.status_code, 200)


class URLResolutionTests(TestCase):
    """Smoke test every public URL to confirm 200 (or 302) responses."""

    URLS = [
        'home', 'about', 'project_list', 'education',
        'contact', 'bussiness_card', 'tipping',
        'robots_txt', 'sitemap_xml',
    ]

    def test_all_public_urls_resolve(self):
        for name in self.URLS:
            with self.subTest(url_name=name):
                resp = self.client.get(reverse(name))
                self.assertIn(resp.status_code, [200, 302],
                              msg=f"URL '{name}' returned {resp.status_code}")


class SEORoutesTests(TestCase):

    def test_robots_txt(self):
        resp = self.client.get(reverse('robots_txt'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/plain')
        self.assertIn(b'User-agent: *', resp.content)
        self.assertIn(b'Sitemap:', resp.content)

    def test_sitemap_xml(self):
        Project.objects.create(
            title='Sample Project',
            slug='sample-project',
            description='Sample description',
            is_published=True
        )
        resp = self.client.get(reverse('sitemap_xml'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/xml')
        self.assertIn(b'<urlset', resp.content)
        self.assertIn(b'/projects/', resp.content)

