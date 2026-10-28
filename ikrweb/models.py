"""
ikrweb/models.py

Data models for Isaac Rono's portfolio.
Derived from ikr2026.docx: Senior Software Engineer & Enterprise Systems Consultant.

Models:
  - About          : Singleton profile / contact / social / resume
  - Skill          : Technical and professional skills by category
  - Experience     : Professional experience entries from the CV
  - Education      : Formal education records
  - Certification  : Professional certifications (e.g. Sage Intacct)
  - Project        : Portfolio projects with featured/published flags
  - Contact        : Inbound consultation requests from the contact form
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone


# ---------------------------------------------------------------------------
# About (Singleton profile record)
# ---------------------------------------------------------------------------

class About(models.Model):
    """
    Singleton model. Should have exactly one record.
    Provides the identity, contact details, social links, and documents
    shown across the entire site.
    """
    name             = models.CharField(max_length=100)
    title            = models.CharField(max_length=200, help_text="Professional headline shown in the hero section")
    bio              = models.TextField(help_text="Executive summary / about paragraph")
    profile_image    = models.ImageField(upload_to='profile/', blank=True, null=True)
    resume           = models.FileField(upload_to='documents/', blank=True, null=True)
    favicon          = models.ImageField(upload_to='branding/', blank=True, null=True)

    # Contact
    email            = models.EmailField()
    phone            = models.CharField(max_length=30, blank=True)
    location         = models.CharField(max_length=150, blank=True)
    website          = models.URLField(blank=True, help_text="Public website URL shown on the business card")

    # Social
    linkedin         = models.URLField(blank=True)
    github           = models.URLField(blank=True)
    twitter          = models.URLField(blank=True)
    instagram        = models.URLField(blank=True)
    youtube          = models.URLField(blank=True)

    # M-Pesa tipping
    mpesa_number     = models.CharField(
        max_length=20, blank=True,
        help_text="M-Pesa number for the tipping page, e.g. 0705027739"
    )
    mpesa_name       = models.CharField(
        max_length=100, blank=True,
        help_text="Account name shown on the tipping page"
    )

    class Meta:
        verbose_name_plural = "About"

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

class Skill(models.Model):
    BEGINNER     = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED     = 'advanced'
    EXPERT       = 'expert'

    SKILL_LEVELS = [
        (BEGINNER,     'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED,     'Advanced'),
        (EXPERT,       'Expert'),
    ]

    name     = models.CharField(max_length=100)
    level    = models.CharField(max_length=20, choices=SKILL_LEVELS, default=INTERMEDIATE)
    category = models.CharField(
        max_length=100,
        help_text="Grouping label, e.g. 'Enterprise ERP & Consulting', 'Software Engineering'"
    )
    icon     = models.CharField(
        max_length=50, blank=True,
        help_text="Font Awesome icon name without 'fa-', e.g. 'database', 'code', 'server'"
    )
    order    = models.PositiveSmallIntegerField(default=0, help_text="Display order within category")

    class Meta:
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"

    @property
    def level_percentage(self):
        """Returns the skill level as a percentage integer for progress bars."""
        mapping = {
            self.BEGINNER:     25,
            self.INTERMEDIATE: 50,
            self.ADVANCED:     75,
            self.EXPERT:       100,
        }
        return mapping.get(self.level, 50)


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

class Experience(models.Model):
    """
    Professional experience entry matching the CV in ikr2026.docx.
    """
    job_title    = models.CharField(max_length=200)
    company      = models.CharField(max_length=200)
    location     = models.CharField(max_length=150, blank=True)
    start_date   = models.DateField()
    end_date     = models.DateField(
        blank=True, null=True,
        help_text="Leave blank if this is the current position"
    )
    is_current   = models.BooleanField(
        default=False,
        help_text="Tick if this is the current role (end_date will be ignored in display)"
    )
    description  = models.TextField(
        help_text="Responsibilities, achievements, and technologies used. "
                  "Each bullet point on a new line."
    )

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.job_title} at {self.company}"

    @property
    def duration_label(self):
        end = "Present" if self.is_current else (
            self.end_date.strftime("%b %Y") if self.end_date else ""
        )
        return f"{self.start_date.strftime('%b %Y')} – {end}"


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

class Education(models.Model):
    institution    = models.CharField(max_length=200)
    degree         = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=150, blank=True)
    start_date     = models.DateField()
    end_date       = models.DateField(blank=True, null=True)
    description    = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} — {self.institution}"


# ---------------------------------------------------------------------------
# Certification
# ---------------------------------------------------------------------------

class Certification(models.Model):
    """
    Professional certifications. e.g. Sage Intacct Implementation Consultant.
    """
    name         = models.CharField(max_length=200)
    issuer       = models.CharField(max_length=200, blank=True)
    issued_date  = models.DateField(blank=True, null=True)
    expiry_date  = models.DateField(blank=True, null=True, help_text="Leave blank if it does not expire")
    credential_id = models.CharField(max_length=200, blank=True)
    credential_url = models.URLField(blank=True)

    class Meta:
        ordering = ['-issued_date']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class Project(models.Model):
    """
    Portfolio project entry. Featured projects appear on the home page.
    Published controls public visibility.
    """
    title        = models.CharField(max_length=200)
    slug         = models.SlugField(max_length=220, unique=True, blank=True)
    description  = models.TextField()
    image        = models.ImageField(upload_to='projects/', blank=True, null=True)
    technologies = models.CharField(
        max_length=500,
        help_text="Comma-separated list of technologies, e.g. 'Django, Python, PostgreSQL'"
    )
    github_url   = models.URLField(blank=True, null=True)
    live_url     = models.URLField(blank=True, null=True)
    featured     = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True,
                                       help_text="Unpublished projects are hidden from the public site")
    created_at   = models.DateTimeField(default=timezone.now)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

    def get_technologies_list(self):
        """Returns technologies as a clean list for template iteration."""
        return [t.strip() for t in self.technologies.split(',') if t.strip()]


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

class Contact(models.Model):
    """
    Inbound consultation request from the contact form.
    """
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"