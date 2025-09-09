# Pollify - Real-time Polling Platform

## Overview

Pollify is a real-time polling platform built with Flask that allows users to create interactive polls, share them via QR codes, and view live results. The application features user authentication, admin management capabilities, and real-time updates using WebSocket connections. Users can create polls with multiple options, share them with unique codes, and see voting results update in real-time as participants cast their votes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with Python
- **Real-time Communication**: Flask-SocketIO for WebSocket connections enabling live poll result updates
- **Database**: SQLite with SQLAlchemy ORM for data persistence
- **Authentication**: Session-based authentication with password hashing using Werkzeug
- **Database Schema**: Relational design with User, Poll, PollOption, and Vote models with proper foreign key relationships

### Frontend Architecture
- **Template Engine**: Jinja2 templating with Flask
- **UI Framework**: Bootstrap with dark theme styling
- **Real-time Updates**: Socket.IO client for live poll result synchronization
- **Charts**: Chart.js for visualizing poll results
- **Icons**: Feather Icons for consistent iconography
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Data Storage
- **Primary Database**: SQLite database (pollify.db) with SQLAlchemy models
- **Models**: User (with admin capabilities), Poll (with share codes), PollOption, and Vote entities
- **Relationships**: One-to-many relationships between users and polls, polls and options, polls and votes
- **Session Management**: Flask sessions for user authentication state

### Security & Authentication
- **User Management**: Registration, login, and admin user system
- **Password Security**: Werkzeug password hashing for secure credential storage
- **Admin Panel**: Dedicated admin dashboard for user and poll management
- **Session Security**: Session-based authentication with configurable secret keys

### Key Features
- **Poll Creation**: Users can create polls with multiple custom options
- **Share System**: Unique share codes and QR code generation for easy poll distribution
- **Real-time Voting**: Live vote counting with instant result updates via WebSockets
- **Result Visualization**: Interactive charts showing poll results and statistics
- **Admin Controls**: Administrative interface for managing users and polls

## External Dependencies

### Python Packages
- **Flask**: Web framework for routing and request handling
- **Flask-SocketIO**: WebSocket support for real-time communication
- **Flask-SQLAlchemy**: Database ORM and management
- **Werkzeug**: Password hashing and security utilities
- **qrcode**: QR code generation for poll sharing
- **Pillow**: Image processing for QR code creation

### Frontend Libraries
- **Bootstrap**: UI framework with dark theme from Replit CDN
- **Chart.js**: Data visualization for poll results
- **Socket.IO**: Client-side WebSocket communication
- **Feather Icons**: Icon library for consistent UI elements

### Database
- **SQLite**: File-based database for development and deployment simplicity
- **SQLAlchemy**: ORM layer with declarative base for model definitions

### Development Tools
- **Debug Mode**: Flask development server with hot reloading
- **Logging**: Python logging for debugging and monitoring
- **CORS**: Cross-origin resource sharing enabled for Socket.IO connections