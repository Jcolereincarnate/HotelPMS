# AI-Powered Hotel Management System

## Description
The AI-Powered Hotel Management System is a modern web-based application designed to streamline hotel operations by providing a faster, more intuitive, and data-driven alternative to traditional Property Management Systems (PMS) such as Opera. The system focuses on automation, usability, and analytics to improve operational efficiency and guest experience.

---

## Main Features
- Smart guest check-in and check-out management
- Room booking and availability tracking
- Automated billing and invoice generation
- Housekeeping status management
- Guest profile and history management
- Admin dashboard with analytics and insights
- AI-powered data analysis for pricing, occupancy, and guest behavior
- Clean and responsive user interface

---

## Tech Stack
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS
- **Database:** SQLite (development), PostgreSQL (production-ready)
- **AI Integration:** Meta Llama AI model (for analytics and insights)
- **Authentication:** Django Authentication System
- **Deployment:** Render / Vercel (optional)

---

## Installation Steps

1. Clone the repository:
```bash 
git clone https://github.com/Jcolereincarnate/HotelPMS.git
cd hotel-management-system
```
2.	Create and activate a virtual environment:
    python -m venv venv
    source venv/bin/activate   
3.	Install dependencies:
    pip install -r requirements.txt
4.	Create a .env file in the project root.
5.	Run database migrations:
    python manage.py migrate
6.	Create a superuser:
    python manage.py createsuperuser

How to Run the Project

Start the development server:
    python manage.py runserver
Open your browser and visit:
    http://127.0.0.1:8000/
Admin panel:
    http://127.0.0.1:8000/admin/

Author

Tope Okubule
Computer Science Student | Software Engineer| IT support specialist
Passionate about backend systems, AI integration, and scalable web applications