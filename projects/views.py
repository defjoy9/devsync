# projects/views.py
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ClickUpTokenForm
from projects.models import Profile
from datetime import datetime


@login_required
def set_clickup_token(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ClickUpTokenForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('projects:clickup_tasks')  # go see tasks
    else:
        form = ClickUpTokenForm(instance=profile)
    return render(request, 'projects/set_token.html', {'form': form})


@login_required
def clickup_tasks(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    token = profile.clickup_token

    if not token:
        return redirect('projects:set_clickup_token')

    headers = {'Authorization': token}
    tasks = []

    # Step 1: Get user info
    user_resp = requests.get('https://api.clickup.com/api/v2/user', headers=headers)
    if user_resp.ok:
        user_data = user_resp.json()['user']

        # Step 2: Get all teams
        teams_resp = requests.get('https://api.clickup.com/api/v2/team', headers=headers)
        if teams_resp.ok:
            teams = teams_resp.json().get('teams', [])

            # Step 3: Get tasks for each team assigned to this user
            for team in teams:
                team_id = team['id']
                tasks_resp = requests.get(
                    f'https://api.clickup.com/api/v2/team/{team_id}/task?assignee={user_data["id"]}',
                    headers=headers
                )
                if tasks_resp.ok:
                    team_tasks = tasks_resp.json().get('tasks', [])
                    for t in team_tasks:
                        due_date_ms = t.get('due_date')
                        due_date = datetime.fromtimestamp(int(due_date_ms)/1000).strftime('%Y-%m-%d') if due_date_ms else 'No due date'
                        tasks.append({
                            'name': t['name'],
                            'status': t['status']['status'],
                            'due_date': due_date
                        })

    return render(request, 'projects/clickup_tasks.html', {'tasks': tasks})
