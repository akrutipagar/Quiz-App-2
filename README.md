# Quiz-Master-App

Description :
This project implements a full-stack quiz management system that supports user and 
admin roles, enabling quiz creation, participation, and performance tracking. The 
system features scheduled reports, secure authentication, and content management. 
Technologies Used :- 
• Backend: Python (Flask), SQLAlchemy, Flask-Mail, Flask-Login, Celery 
• Frontend: Vue.js (with Axios) 
• Database: SQLite 
• Task Scheduling: Celery + Redis 
Purpose Behind Technologies  :-
• Flask: Lightweight and modular backend framework for API development. 
• Flask-Login: Handles session-based user authentication and role-based 
access. 
• Flask-Mail: Sends performance reports and reminders via email. 
• SQLAlchemy: ORM for managing relational database interactions efficiently. 
• Celery + Redis: Handles daily/recurring background tasks like email reminders. 
• Vue.js: Reactive frontend framework for dynamic dashboards and form-based 
CRUD operations
• SQLite: Lightweight local DB ideal for fast prototyping and academic 
applications. 
• Flask (app.py): Core backend API logic, authentication, and routing. 
• Frontend (Vue.js): Admin dashboard, user interface, and routing logic. 
• Celery & Redis: Handles asynchronous background tasks like reminders and 
reports. 
• Flask-Mail: Manages transactional and scheduled email delivery. 
• SQLAlchemy ORM: Used for database modeling and relational mappings.
