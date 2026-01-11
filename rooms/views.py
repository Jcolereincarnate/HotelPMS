# rooms/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from core.decorators import role_required
from .models import Room, RoomType, HousekeepingTask
from .forms import RoomForm, RoomTypeForm, HousekeepingTaskForm, UpdateTaskStatusForm

@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def room_list(request):
    status_filter = request.GET.get('status', '')
    floor_filter = request.GET.get('floor', '')
    
    rooms = Room.objects.select_related('room_type').order_by('floor', 'room_number')
    
    if status_filter:
        rooms = rooms.filter(status=status_filter)
    
    if floor_filter:
        rooms = rooms.filter(floor=floor_filter)
    
    floors = Room.objects.values_list('floor', flat=True).distinct().order_by('floor')
    
    context = {
        'title': 'Room Management',
        'rooms': rooms,
        'status_filter': status_filter,
        'floor_filter': floor_filter,
        'floors': floors,
        'status_choices': Room._meta.get_field('status').choices,
    }
    return render(request, 'rooms/room_list.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    roomtype=room.room_type
    current_reservation = room.reservations.filter(status='checked_in').first()
    pending_tasks = room.housekeeping_tasks.filter(status__in=['pending', 'in_progress']).order_by('-priority', 'due_date')
    
    context = {
        'title': f'Room {room.room_number}',
        'roomtype': roomtype,
        'room': room,
        'current_reservation': current_reservation,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'rooms/room_detail.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f'Room {room.room_number} created successfully')
            return redirect('room_detail', pk=room.pk)
    else:
        form = RoomForm()
    
    context = {
        'title': 'Create Room',
        'form': form,
    }
    return render(request, 'rooms/create_room.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def edit_room(request, pk):
    room = get_object_or_404(Room, pk=pk)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            messages.success(request, 'Room updated successfully')
            return redirect('room_detail', pk=room.pk)
    else:
        form = RoomForm(instance=room)
    
    context = {
        'title': f'Edit Room {room.room_number}',
        'form': form,
        'room': room,
    }
    return render(request, 'rooms/edit_room.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def delete_room(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        room.delete()
        messages.success(request, f'Room {room.room_number} deleted successfully.')
        return redirect('room_list') 

    context = {
        'title': f'Delete Room {room.room_number}',
        'room': room,
    }
    return render(request, 'rooms/delete_room.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def housekeeping_dashboard(request):
    priority_filter = request.GET.get('priority', '')
    status_filter = request.GET.get('status', '')
    
    tasks = HousekeepingTask.objects.select_related('room', 'assigned_to').order_by('-priority', 'due_date')
    
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if request.user.role == 'housekeeping':
        tasks = tasks.filter(assigned_to=request.user)
    
    context = {
        'title': 'Housekeeping Tasks',
        'tasks': tasks,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'priority_choices': HousekeepingTask.PRIORITY_CHOICES,
        'status_choices': HousekeepingTask.STATUS_CHOICES,
    }
    return render(request, 'rooms/housekeeping_dashboard.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def create_housekeeping_task(request):
    if request.method == 'POST':
        form = HousekeepingTaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task created and assigned successfully')
            return redirect('housekeeping_tasks')
    else:
        form = HousekeepingTaskForm()
    
    context = {
        'title': 'Create Housekeeping Task',
        'form': form,
    }
    return render(request, 'rooms/create_task.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def housekeeping_task_detail(request, pk):
    task = get_object_or_404(HousekeepingTask, pk=pk)
    
    if request.method == 'POST':
        form = UpdateTaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            if task.status == 'completed':
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, 'Task status updated')
            return redirect('housekeeping_dashboard')
    else:
        form = UpdateTaskStatusForm(instance=task)
    
    context = {
        'title': f'Task: {task.task_type}',
        'task': task,
        'form': form,
    }
    return render(request, 'rooms/task_detail.html', context)
@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def edit_housekeeping_task(request, pk):
    task = get_object_or_404(HousekeepingTask, pk=pk)

    if request.method == 'POST':
        form = HousekeepingTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully")
            return redirect('task_detail', pk=task.pk)
    else:
        form = HousekeepingTaskForm(instance=task)

    context = {
        'title': f'Edit Task: {task.task_type}',
        'task': task,
        'form': form,
    }
    return render(request, 'rooms/edit_task.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def delete_housekeeping_task(request, pk):
    task = get_object_or_404(HousekeepingTask, pk=pk)

    if request.method == 'POST':
        task.delete()
        messages.success(request, "Task deleted successfully")
        return redirect('housekeeping_tasks')

    context = {
        'title': f'Delete Task: {task.task_type}',
        'task': task,
    }
    return render(request, 'rooms/delete_task.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def update_housekeeping_task(request, pk):
    task = get_object_or_404(HousekeepingTask, pk=pk)
    if request.method == 'POST':
        form = UpdateTaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully')
            return redirect('task_detail', pk=task.pk)
    else:
        form = UpdateTaskStatusForm(instance=task)

    context = {
        'title': 'Update Task',
        'task': task,
        'form': form,
    }
    return render(request, 'rooms/task_update.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def change_room_status(request, pk):
    room = get_object_or_404(Room, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Room.STATUS_CHOICES):
        room.status = new_status
        room.save()
        messages.success(request, f'Room {room.room_number} status updated to {room.get_status_display()}')
    
    return redirect('room_detail', pk=pk)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def room_occupancy_report(request):
    total_rooms = Room.objects.count()
    occupied = Room.objects.filter(status='occupied').count()
    available = Room.objects.filter(status='available').count()
    maintenance = Room.objects.filter(status='maintenance').count()
    cleaning = Room.objects.filter(status='cleaning').count()
    
    occupancy_rate = (occupied / total_rooms * 100) if total_rooms > 0 else 0
    
    rooms_by_type = RoomType.objects.annotate(count=Count('rooms'))
    
    context = {
        'title': 'Room Occupancy Report',
        'total_rooms': total_rooms,
        'occupied': occupied,
        'available': available,
        'maintenance': maintenance,
        'cleaning': cleaning,
        'occupancy_rate': round(occupancy_rate, 2),
        'rooms_by_type': rooms_by_type,
    }
    return render(request, 'rooms/occupancy_report.html', context)

login_required(login_url='login')
@role_required(['admin', 'manager', 'housekeeping'])
def create_room_type(request):
    if request.method == 'POST':
        form = RoomTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room type created successfully.')
            return redirect('room_list')
    else:
        form = RoomTypeForm()

    context = {'form': form, 'title': 'Create Room Type'}
    return render(request, 'rooms/create_room_type.html', context)