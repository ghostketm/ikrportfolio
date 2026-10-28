"""
ikrweb/views.py

All views for Isaac Rono's portfolio.

Each view fetches the minimal required data and passes it to its template
via a well-defined context dict documented in the frontend data contract.
"""

import logging

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .models import About, Certification, Contact, Education, Experience, Project, Skill

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_about():
    """
    Returns the singleton About record (or None).
    Called by every view so the base template always has access to it.
    """
    return About.objects.first()


# ---------------------------------------------------------------------------
# Public views
# ---------------------------------------------------------------------------

def home(request):
    """
    Homepage.

    Context:
        about              – About singleton (or None)
        featured_projects  – Top 3 newest and recently updated published projects (with fallback)
        skills             – All skills ordered by category/order
        project_count      – Total published project count (for stats widget)
        skill_count        – Total skill count (for stats widget)
    """
    about = _get_about()
    
    # Query published projects ordered by latest updates / additions (top 3)
    # Prioritizes featured ones if available, otherwise latest additions/updates
    featured_projects = list(
        Project.objects.filter(featured=True, is_published=True)
        .order_by('-updated_at', '-created_at')[:3]
    )
    if len(featured_projects) < 3:
        existing_ids = [p.id for p in featured_projects]
        additional_projects = list(
            Project.objects.filter(is_published=True)
            .exclude(id__in=existing_ids)
            .order_by('-updated_at', '-created_at')[:(3 - len(featured_projects))]
        )
        featured_projects.extend(additional_projects)
    skills = Skill.objects.all()

    context = {
        'about': about,
        'featured_projects': featured_projects,
        'skills': skills,
        'project_count': Project.objects.filter(is_published=True).count(),
        'skill_count': skills.count(),
    }
    return render(request, 'ikrweb/home.html', context)


def about(request):
    """
    About / profile page.

    Context:
        about      – About singleton (or None)
        skills     – All skills ordered by category/order
        experience – Professional experience entries (newest first)
    """
    about = _get_about()
    skills = Skill.objects.all()
    experience = Experience.objects.all()

    context = {
        'about': about,
        'skills': skills,
        'experience': experience,
    }
    return render(request, 'ikrweb/about.html', context)


def project_list(request):
    """
    Full project listing (published only). Supports optional search and technology filter.

    Context:
        projects          – QuerySet of published projects, newest first
        search_query      – Currently searched keyword
        tech_filter       – Selected technology or ''
    """
    projects = Project.objects.filter(is_published=True).order_by('-created_at')
    
    search = request.GET.get('q', '').strip()
    tech = request.GET.get('tech', '').strip()

    if search:
        projects = projects.filter(title__icontains=search) | projects.filter(description__icontains=search)
    if tech:
        projects = projects.filter(technologies__icontains=tech)

    context = {
        'projects': projects,
        'search_query': search,
        'tech_filter': tech,
    }
    return render(request, 'ikrweb/project_list.html', context)


def project_detail(request, pk):
    """
    Individual project detail (published projects only).

    Context:
        project – Project instance
    """
    project = get_object_or_404(Project, pk=pk, is_published=True)

    context = {
        'project': project,
    }
    return render(request, 'ikrweb/project_detail.html', context)


def education(request):
    """
    Education & certifications page.

    Context:
        education_list  – Education records, newest first
        certifications  – Certification records, newest first
    """
    education_list = Education.objects.all()
    certifications = Certification.objects.all()

    context = {
        'education_list': education_list,
        'certifications': certifications,
    }
    return render(request, 'ikrweb/education.html', context)


def business_card(request):
    """
    Digital business card page.

    Context:
        about  – About singleton (or None)
        skills – All skills (for the skills strip on the card)
    """
    about = _get_about()
    skills = Skill.objects.all()

    context = {
        'about': about,
        'skills': skills,
    }
    return render(request, 'ikrweb/bc.html', context)


def tipping(request):
    """
    M-Pesa tipping / support page.

    Context:
        about – About singleton (provides mpesa_number, mpesa_name)
    """
    about = _get_about()

    context = {
        'about': about,
    }
    return render(request, 'ikrweb/tipping.html', context)


def contact(request):
    """
    Consultation / contact page.

    GET  – Renders the empty contact form.
    POST – Validates, saves the submission, attempts email notification,
           and redirects back with a success message.

    Context:
        form   – ContactForm instance
        about  – About singleton (for the static contact info block)
    """
    about = _get_about()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save()

            # Attempt email notification to the site owner.
            # Failure is logged but does not break the user flow.
            owner_email = getattr(settings, 'CONTACT_EMAIL', None) or (
                about.email if about else None
            )
            if owner_email:
                try:
                    send_mail(
                        subject=f"[Portfolio Consult] {submission.subject}",
                        message=(
                            f"From: {submission.name} <{submission.email}>\n\n"
                            f"{submission.message}"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[owner_email],
                        fail_silently=False,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Contact email failed to send: %s", exc)

            messages.success(
                request,
                "Thank you for reaching out! I will get back to you soon."
            )
            return redirect('contact')
    else:
        form = ContactForm()

    context = {
        'form': form,
        'about': about,
    }
    return render(request, 'ikrweb/contact.html', context)


# ---------------------------------------------------------------------------
# SEO & System Views
# ---------------------------------------------------------------------------

def robots_txt(request):
    """
    Renders robots.txt for search engine crawlers.
    """
    return render(request, 'robots.txt', content_type='text/plain')


def sitemap_xml(request):
    """
    Renders dynamic XML sitemap including all live projects and public pages.
    """
    projects = Project.objects.filter(is_published=True).order_by('-created_at')
    base_url = request.build_absolute_uri('/')[:-1]
    return render(
        request,
        'sitemap.xml',
        {'projects': projects, 'base_url': base_url},
        content_type='application/xml'
    )