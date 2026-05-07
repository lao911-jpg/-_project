from django.db import models
from django.utils import timezone
from datetime import timedelta

class Engineer(models.Model):
    name = models.CharField(max_length=100)
    work_start = models.TimeField(default='09:00:00')
    work_end = models.TimeField(default='18:00:00')
    
    def __str__(self):
        return self.name

class Competence(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class EngineerCompetence(models.Model):
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE)
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE)
    avg_solve_time_minutes = models.IntegerField(help_text="Сколько минут инженер решает задачу этой компетенции")
    
    class Meta:
        unique_together = ('engineer', 'competence')
    
    def __str__(self):
        return f"{self.engineer.name} - {self.competence.name}: {self.avg_solve_time_minutes} мин"

class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('assigned', 'Назначена'),
        ('done', 'Выполнена'),
        ('violated', 'Просрочена'),
    ]
    
    required_competence = models.ForeignKey(Competence, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    sla_deadline = models.DateTimeField()
    assigned_engineer = models.ForeignKey(Engineer, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    
    def __str__(self):
        return f"Заявка #{self.id} | {self.priority} | {self.required_competence.name}"
    
    def save(self, *args, **kwargs):
        # Автоматически вычисляем дедлайн по приоритету
        if not self.sla_deadline and self.created_at:
            if self.priority == 'high':
                self.sla_deadline = self.created_at + timedelta(hours=1)
            elif self.priority == 'medium':
                self.sla_deadline = self.created_at + timedelta(hours=4)
            else:  # low
                self.sla_deadline = self.created_at + timedelta(days=2)
        super().save(*args, **kwargs)