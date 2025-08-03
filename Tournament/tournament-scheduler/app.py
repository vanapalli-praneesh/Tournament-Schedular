from flask import Flask, render_template, request, redirect, url_for, session
from crud_operations import MatchScheduler, insert_tournament, insert_match, fetch_tournament_by_id, fetch_matches_by_tournament, update_match_in_db, fetch_all_tournaments, delete_tournament_by_id
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session


@app.route('/')
def root():
    return redirect(url_for('create_tournament'))


from datetime import date, timedelta

@app.route('/create_tournament', methods=['GET', 'POST'])
def create_tournament():
    error = None
    min_start_date = date.today()
    min_start_date_str = min_start_date.isoformat()
    min_end_date = min_start_date + timedelta(days=1)
    min_end_date_str = min_end_date.isoformat()

    if request.method == 'POST':
        name = request.form.get('tournament_name', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()
        description = request.form.get('description', '').strip()

        if not name or not start_date or not end_date:
            error = "Please fill out all required fields."
        elif end_date <= start_date:
            error = "End date must be after the start date."
        elif start_date < min_start_date_str:
            error = "Start date cannot be earlier than today."
        else:
            tournament_id = insert_tournament(name, start_date, end_date, description)
            session['tournament_id'] = tournament_id
            return redirect(url_for('index'))

    return render_template(
        'create_tournament.html',
        error=error,
        min_start_date=min_start_date_str,
        min_end_date=min_end_date_str,
    )



@app.route('/index')
def index():
    tournament_id = session.get('tournament_id')
    if not tournament_id:
        return redirect(url_for('create_tournament'))
    tournament = fetch_tournament_by_id(tournament_id)
    return render_template('index.html', tournament=tournament)


@app.route('/generate', methods=['GET', 'POST'])
def generate_matches():
    tournament_id = session.get('tournament_id')
    if not tournament_id:
        return redirect(url_for('create_tournament'))
    if request.method == 'POST':
        teams = request.form.get('teams').split(',')
        teams = [team.strip() for team in teams if team.strip()]
        match_id = 1
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                insert_match(tournament_id, teams[i], teams[j])
                match_id += 1
        return redirect(url_for('schedule_matches'))
    return render_template('generate_matches.html')

@app.route('/schedule', methods=['GET', 'POST'])
def schedule_matches():
    tournament_id = session.get('tournament_id')
    if not tournament_id:
        return redirect(url_for('create_tournament'))
    matches = fetch_matches_by_tournament(tournament_id)
    error = None
    tournament = fetch_tournament_by_id(tournament_id)
    tournament_start = tournament['start_date']
    tournament_end = tournament['end_date']
    try:
        tournament_start_date = datetime.strptime(tournament_start, "%Y-%m-%d").date()
        tournament_end_date = datetime.strptime(tournament_end, "%Y-%m-%d").date()
    except Exception:
        error = "Tournament start or end date not configured correctly."
        return render_template(
            'schedule_matches.html',
            matches=matches,
            error=error,
            tournament_start=tournament_start,
            tournament_end=tournament_end,
        )
    if request.method == 'POST':
        for match in matches:
            date_str = request.form.get(f'date_{match["id"]}')
            time_str = request.form.get(f'time_{match["id"]}')
            location_str = request.form.get(f'location_{match["id"]}', '')
            duration_str = request.form.get(f'duration_{match["id"]}')
            if not date_str or not time_str:
                error = f"Match {match['id']}: Please enter both date and time."
                break
            if not duration_str:
                error = f"Match {match['id']}: Please select a duration."
                break
            try:
                match_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                duration = int(duration_str)
                if duration < 1 or duration > 10:
                    error = f"Match {match['id']}: Duration must be between 1 and 10 hours."
                    break
            except ValueError:
                error = f"Match {match['id']}: Invalid date format or duration."
                break
            if match_date < tournament_start_date or match_date > tournament_end_date:
                error = (
                    f"Match {match['id']} date {date_str} is outside tournament dates "
                    f"({tournament_start} to {tournament_end})."
                )
                break
            update_match_in_db(match['id'], date_str, time_str, location_str, duration)
        if error:
            # Re-fetch matches to preserve input values
            matches = fetch_matches_by_tournament(tournament_id)
            for match in matches:
                match['date'] = request.form.get(f'date_{match["id"]}', match['date'])
                match['time'] = request.form.get(f'time_{match["id"]}', match['time'])
                match['location'] = request.form.get(f'location_{match["id"]}', match['location'])
                match['duration'] = request.form.get(f'duration_{match["id"]}', match.get('duration', 1))
            return render_template(
                'schedule_matches.html',
                matches=matches,
                error=error,
                tournament_start=tournament_start,
                tournament_end=tournament_end,
            )
        return redirect(url_for('view_matches'))
    return render_template(
        'schedule_matches.html',
        matches=matches,
        tournament_start=tournament_start,
        tournament_end=tournament_end,
        error=error,
    )

@app.route('/view')
def view_matches():
    tournament_id = session.get('tournament_id')
    if not tournament_id:
        return redirect(url_for('create_tournament'))
    matches = fetch_matches_by_tournament(tournament_id)
    return render_template('view_matches.html', matches=matches)

@app.route('/update/<int:match_id>', methods=['GET', 'POST'])
def update_match(match_id):
    tournament_id = session.get('tournament_id')
    if not tournament_id:
        return redirect(url_for('create_tournament'))
    matches = fetch_matches_by_tournament(tournament_id)
    match = next((m for m in matches if m['id'] == match_id), None)
    if not match:
        return redirect(url_for('view_matches'))
    error = None
    tournament = fetch_tournament_by_id(tournament_id)
    if request.method == 'POST':
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        location_str = request.form.get('location', '')
        duration_str = request.form.get('duration')
        if not date_str or not time_str:
            error = "Both date and time are required."
        elif not duration_str:
            error = "Duration is required."
        else:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                duration = int(duration_str)
                if duration < 1 or duration > 10:
                    error = "Duration must be between 1 and 10 hours."
                else:
                    start_date = datetime.strptime(tournament['start_date'], "%Y-%m-%d").date()
                    end_date = datetime.strptime(tournament['end_date'], "%Y-%m-%d").date()
                    if date_obj < start_date or date_obj > end_date:
                        error = f"Date must be between {start_date} and {end_date}."
                    else:
                        update_match_in_db(match_id, date_str, time_str, location_str, duration)
                        return redirect(url_for('view_matches'))
            except Exception:
                error = "Invalid date, time, or duration format."
        return render_template('update_matches.html', match=match, error=error,
                               tournament_start=tournament['start_date'],
                               tournament_end=tournament['end_date'])
    return render_template(
        'update_matches.html',
        match=match,
        tournament_start=tournament['start_date'],
        tournament_end=tournament['end_date'],
        error=error
    )

@app.route('/check_conflicts')
def check_conflicts():
    tournament_id = session.get('tournament_id')
    if not tournament_id:
        return redirect(url_for('create_tournament'))
    matches = fetch_matches_by_tournament(tournament_id)
    conflicts = []
    match_schedule = {}
    
    for match in matches:
        # Only consider matches that have all required fields
        if match['date'] and match['time'] and match['location'] and match['duration']:
            # Create key with all four parameters: date, time, duration, venue
            key = (match['date'], match['time'], match['duration'], match['location'])
            if key not in match_schedule:
                match_schedule[key] = []
            match_schedule[key].append(match)
    
    for key, conflict_matches in match_schedule.items():
        if len(conflict_matches) > 1:
            conflicts.append((key, conflict_matches))
    
    return render_template('check_conflicts.html', conflicts=conflicts)

@app.route('/tournaments')
def tournaments():
    tournaments = fetch_all_tournaments()
    return render_template('tournaments.html', tournaments=tournaments)

@app.route('/tournaments/<int:tournament_id>/delete', methods=['POST'])
def delete_tournament(tournament_id):
    delete_tournament_by_id(tournament_id)
    return redirect(url_for('tournaments'))

@app.route('/tournaments/<int:tournament_id>/matches')
def tournament_matches(tournament_id):
    tournament = fetch_tournament_by_id(tournament_id)
    matches = fetch_matches_by_tournament(tournament_id)
    return render_template('tournament_matches.html', tournament=tournament, matches=matches)


if __name__ == '__main__':
    app.run(debug=True)
