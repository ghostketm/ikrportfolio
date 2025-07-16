from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Project, About, Skill, Contact, Education
from .forms import ContactForm

def home(request):
    """Homepage view with featured projects"""
    featured_projects = Project.objects.filter(featured=True)[:3]
    about = About.objects.first()
    skills = Skill.objects.all()
    
    context = {
        'featured_projects': featured_projects,
        'about': about,
        'skills': skills,
    }
    return render(request, 'ikrweb/home.html', context)

def about(request):
    """About page view"""
    about = About.objects.first()
    skills = Skill.objects.all()
    
    context = {
        'about': about,
        'skills': skills,
    }
    return render(request, 'ikrweb/about.html', context)

def project_list(request):
    """Projects listing page"""
    projects = Project.objects.all()
    
    context = {
        'projects': projects,
    }
    return render(request, 'ikrweb/project_list.html', context)

def project_detail(request, pk):
    """Individual project detail page"""
    project = get_object_or_404(Project, pk=pk)
    
    context = {
        'project': project,
    }
    return render(request, 'ikrweb/project_detail.html', context)

def education(request):
    """Education page view"""
    education_list = Education.objects.all()
    
    context = {
        'education_list': education_list,
    }
    return render(request, 'ikrweb/education.html', context)

def bussiness_card(request):
    """Business card page view"""
    about = About.objects.first()
    
    context = {
        'about': about,
    }    
    return render(request, 'ikrweb/bc.html', context)

def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save contact message
            contact = form.save()
            
            # Send email (optional)
            try:
                send_mail(
                    subject=f"Portfolio Contact: {contact.subject}",
                    message=contact.message,
                    from_email=contact.email,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Thank you for your message! I will get back to you soon.')
            except:
                messages.success(request, 'Thank you for your message! I will get back to you soon.')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'ikrweb/contact.html', context)