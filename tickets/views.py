from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from .models import Ticket, Engineer, EngineerCompetence, Competence
from .scheduler import Scheduler
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Главная страница - дашборд"""
    tickets = Ticket.objects.all().order_by('-created_at')[:10]
    engineers = Engineer.objects.all()
    return render(request, 'tickets/index.html', {
        'tickets': tickets,
        'engineers': engineers
    })

def schedule_view(request):
    """Показать расписание всех заявок"""
    tickets = Ticket.objects.filter(status__in=['assigned', 'new']).order_by('start_time')
    return render(request, 'tickets/schedule.html', {'tickets': tickets})

def add_ticket(request):
    """Форма создания новой заявки"""
    if request.method == 'POST':
        competence_id = request.POST.get('competence')
        priority = request.POST.get('priority')
        
        competence = get_object_or_404(Competence, id=competence_id)
        
        ticket = Ticket.objects.create(
            required_competence=competence,
            priority=priority,
            status='new'
        )
        
        assign_ticket(ticket)
        
        messages.success(request, f'Заявка #{ticket.id} создана и назначена!')
        return redirect('schedule')
    
    competences = Competence.objects.all()
    return render(request, 'tickets/add_ticket.html', {'competences': competences})

def assign_ticket(ticket):
    """Логика назначения заявки на инженера"""
    engineer_competences = EngineerCompetence.objects.filter(competence=ticket.required_competence)
    
    available_engineers = []
    for ec in engineer_competences:
        engineer = ec.engineer
        
        last_ticket = Ticket.objects.filter(
            assigned_engineer=engineer,
            status__in=['assigned', 'new']
        ).order_by('-end_time').first()
        
        free_from = last_ticket.end_time if last_ticket else None
        
        available_engineers.append({
            'engineer': engineer,
            'free_from': free_from,
            'solve_time': ec.avg_solve_time_minutes
        })
    
    current_time = timezone.now()
    best = Scheduler.find_best_engineer(ticket, available_engineers, current_time)
    
    if best:
        ticket.assigned_engineer = best['engineer']
        ticket.start_time = best['start_time']
        ticket.end_time = best['finish_time']
        ticket.status = 'assigned'
        ticket.save()
        logger.info(f"Заявка #{ticket.id} назначена на {best['engineer'].name}")
        return True
    else:
        ticket.status = 'new'
        ticket.save()
        logger.error(f"Заявка #{ticket.id} не может быть назначена - нет компетенции")
        return False

def reassign_ticket(request, ticket_id):
    """Ручное переназначение заявки"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        engineer_id = request.POST.get('engineer_id')
        new_engineer = get_object_or_404(Engineer, id=engineer_id)
        
        try:
            ec = EngineerCompetence.objects.get(
                engineer=new_engineer,
                competence=ticket.required_competence
            )
            current_time = timezone.now()
            start_time = max(current_time, timezone.now())
            finish_time = start_time + timedelta(minutes=ec.avg_solve_time_minutes)
            
            ticket.assigned_engineer = new_engineer
            ticket.start_time = start_time
            ticket.end_time = finish_time
            ticket.status = 'assigned'
            ticket.save()
            
            messages.success(request, f'Заявка #{ticket.id} переназначена на {new_engineer.name}')
        except EngineerCompetence.DoesNotExist:
            messages.error(request, f'У {new_engineer.name} нет нужной компетенции!')
        
        return redirect('schedule')
    
    engineers = Engineer.objects.all()
    return render(request, 'tickets/reassign_form.html', {
        'ticket': ticket,
        'engineers': engineers
    })

def auto_assign_all(request):
    """Автоматическое назначение всех новых заявок"""
    new_tickets = Ticket.objects.filter(status='new')
    assigned_count = 0
    for ticket in new_tickets:
        if assign_ticket(ticket):
            assigned_count += 1
    
    messages.success(request, f'Назначено {assigned_count} из {new_tickets.count()} заявок')
    return redirect('schedule')