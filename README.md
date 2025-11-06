# Quiz Master Application

## Overview
Quiz Master is a full-stack quiz management system designed to support both user and administrator roles.  
It enables quiz creation, participation, and performance tracking with integrated task scheduling, secure authentication, and automated reporting.

## Technologies Used

**Backend:** Python (Flask), SQLAlchemy, Flask-Mail, Flask-Login, Celery  
**Frontend:** Vue.js (Axios)  
**Database:** SQLite  
**Task Scheduling:** Celery + Redis

## Technology Rationale

| Component | Purpose |
|------------|----------|
| **Flask** | Lightweight, modular backend framework used to build RESTful APIs and manage application logic. |
| **Flask-Login** | Provides session-based authentication and role management for users and administrators. |
| **Flask-Mail** | Handles transactional and scheduled email notifications such as reports and reminders. |
| **SQLAlchemy** | ORM used to abstract database operations and simplify relational data handling. |
| **Celery + Redis** | Manages asynchronous and recurring background tasks, including daily reminders and monthly performance reports. |
| **Vue.js** | Implements a reactive, component-based front-end for dashboards and form-based CRUD operations. |
| **SQLite** | Serves as a lightweight, file-based database ideal for fast prototyping and academic deployments. |

## System Architecture

### Backend (Flask)
- Implements all REST API endpoints for user, quiz, and admin functionalities.  
- Handles authentication, authorization, and session management.  
- Integrates with Celery and Flask-Mail for asynchronous and scheduled tasks.

### Frontend (Vue.js)
- Provides separate interfaces for administrators and users.  
- Supports quiz creation, modification, and result visualization.  
- Communicates with backend APIs through Axios.

### Background Services (Celery + Redis)
- Executes background tasks such as email delivery and scheduled report generation.  
- Ensures responsiveness by offloading non-critical processes from the main Flask thread.

### Email and Reporting (Flask-Mail)
- Generates and sends daily quiz reminders and monthly performance summaries.  
- Configurable templates for automated communication.

## Features
- Role-based authentication (Admin/User)
- Quiz creation, editing, and management
- User quiz participation and score tracking
- Automated daily and monthly reports
- Email notifications via Flask-Mail
- Lightweight deployment architecture using SQLite and Redis
- Extensible design for additional integrations (e.g., MySQL, PostgreSQL)

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/akrutipagar/Quiz_Master_App.git
   cd Quiz_Master_App
