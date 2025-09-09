import secrets
import qrcode
import io
import base64
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import emit
from app import app, db, socketio
from models import User, Poll, PollOption, Vote
from urllib.parse import urljoin

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    polls = Poll.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', user=user, polls=polls)

@app.route('/create_poll', methods=['GET', 'POST'])
def create_poll():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        question = request.form['question']
        options = request.form.getlist('options')
        
        # Filter out empty options
        options = [opt.strip() for opt in options if opt.strip()]
        
        if len(options) < 2:
            flash('Please provide at least 2 options', 'error')
            return render_template('create_poll.html')
        
        # Generate unique share code
        share_code = secrets.token_urlsafe(10)
        
        # Create poll
        poll = Poll(
            question=question,
            user_id=session['user_id'],
            share_code=share_code
        )
        db.session.add(poll)
        db.session.flush()  # Get the poll ID
        
        # Create options
        for option_text in options:
            option = PollOption(text=option_text, poll_id=poll.id)
            db.session.add(option)
        
        db.session.commit()
        
        flash('Poll created successfully!', 'success')
        return redirect(url_for('poll_detail', share_code=share_code))
    
    return render_template('create_poll.html')

@app.route('/poll/<share_code>')
def poll_detail(share_code):
    poll = Poll.query.filter_by(share_code=share_code).first_or_404()
    
    # Generate QR code
    poll_url = urljoin(request.url_root, url_for('poll_detail', share_code=share_code))
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(poll_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    results = poll.get_results()
    
    return render_template('poll.html', poll=poll, qr_code=img_str, 
                         poll_url=poll_url, results=results)

@app.route('/vote', methods=['POST'])
def vote():
    poll_id = request.form['poll_id']
    option_id = request.form['option_id']
    voter_ip = request.remote_addr
    
    # Check if this IP has already voted
    existing_vote = Vote.query.filter_by(poll_id=poll_id, voter_ip=voter_ip).first()
    if existing_vote:
        return jsonify({'success': False, 'message': 'You have already voted on this poll'})
    
    # Create new vote
    vote = Vote(poll_id=poll_id, option_id=option_id, voter_ip=voter_ip)
    db.session.add(vote)
    db.session.commit()
    
    # Get updated results
    poll = Poll.query.get(poll_id)
    results = poll.get_results()
    
    # Emit real-time update
    socketio.emit('vote_update', {
        'poll_id': poll_id,
        'results': results,
        'total_votes': poll.total_votes()
    }, room=f'poll_{poll_id}')
    
    return jsonify({'success': True, 'results': results, 'total_votes': poll.total_votes()})

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    users = User.query.filter_by(is_admin=False).all()
    polls = Poll.query.all()
    
    # Calculate statistics
    user_stats = []
    for user in users:
        user_polls = Poll.query.filter_by(user_id=user.id).all()
        total_votes = sum(poll.total_votes() for poll in user_polls)
        user_stats.append({
            'user': user,
            'poll_count': len(user_polls),
            'total_votes': total_votes
        })
    
    return render_template('admin_dashboard.html', user_stats=user_stats, polls=polls)

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot delete admin user', 'error')
        return redirect(url_for('admin_dashboard'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_poll/<int:poll_id>')
def delete_poll(poll_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Access denied', 'error')
        return redirect(url_for('login'))
    
    poll = Poll.query.get_or_404(poll_id)
    db.session.delete(poll)
    db.session.commit()
    
    flash('Poll deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@socketio.on('join_poll')
def on_join_poll(data):
    poll_id = data['poll_id']
    join_room(f'poll_{poll_id}')
    emit('joined', {'poll_id': poll_id})

@socketio.on('leave_poll')
def on_leave_poll(data):
    poll_id = data['poll_id']
    leave_room(f'poll_{poll_id}')

# Import join_room and leave_room
from flask_socketio import join_room, leave_room
