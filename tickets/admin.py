from django.contrib import admin
from .models import Engineer, Competence, EngineerCompetence, Ticket

@admin.register(Engineer)
class EngineerAdmin(admin.ModelAdmin):
    list_display = ('name', 'work_start', 'work_end')

@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(EngineerCompetence)
class EngineerCompetenceAdmin(admin.ModelAdmin):
    list_display = ('engineer', 'competence', 'avg_solve_time_minutes')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'required_competence', 'priority', 'status', 'created_at', 'assigned_engineer')
    list_filter = ('priority', 'status', 'required_competence')