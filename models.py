from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    polls = db.relationship(
        "Poll",
        back_populates="creator",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def poll_count(self):
        return len(self.polls)

    @property
    def vote_count(self):
        return sum(poll.total_votes() for poll in self.polls)

    def __repr__(self):
        return f"<User {self.username}>"


class Poll(db.Model):
    __tablename__ = "poll"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    share_code = db.Column(db.String(20), unique=True, nullable=False)

    # Relationships
    creator = db.relationship("User", back_populates="polls")
    options = db.relationship(
        "PollOption",
        back_populates="poll",
        cascade="all, delete-orphan",
        lazy=True,
    )
    votes = db.relationship(
        "Vote",
        back_populates="poll",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def get_results(self):
        """Return poll results as {option_id: {'text': ..., 'votes': ...}}"""
        return {
            option.id: {"text": option.text, "votes": len(option.votes)}
            for option in self.options
        }

    def total_votes(self):
        return len(self.votes)

    def __repr__(self):
        return f"<Poll {self.question}>"


class PollOption(db.Model):
    __tablename__ = "poll_option"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable=False)

    # Relationships
    poll = db.relationship("Poll", back_populates="options")
    votes = db.relationship(
        "Vote",
        back_populates="option",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<PollOption {self.text}>"


class Vote(db.Model):
    __tablename__ = "vote"

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("poll.id"), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey("poll_option.id"), nullable=False)
    voter_ip = db.Column(db.String(45), nullable=False)  # To prevent duplicate votes
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    poll = db.relationship("Poll", back_populates="votes")
    option = db.relationship("PollOption", back_populates="votes")

    def __repr__(self):
        return f"<Vote option={self.option_id} poll={self.poll_id}>"
