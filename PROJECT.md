# 📚 Library Management System

A simple web-based **Library Management System** developed using **Django and Python**. The project allows users to view and manage library books through a clean and simple web interface.

## 🚀 Features

- 📖 View available books
- 🔍 Search and browse books
- ➕ Add new books
- ✏️ Update book details
- 🗑️ Delete books
- 📋 Manage book information
- 💻 Simple and responsive web interface
- 🗄️ Database support using SQLite
- 🔗 Django-based backend

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Django
- **Database:** SQLite
- **Development Tool:** Visual Studio Code
- **Version Control:** Git & GitHub

## 📁 Project Structure

```text
Library-system/
│
├── catalog/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── library/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/harshavardhiniraja27-ops/Library-system.git
```

### 2. Open the Project

```bash
cd Library-system
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply Database Migrations

```bash
python manage.py migrate
```

### 7. Start the Development Server

```bash
python manage.py runserver
```

Open the following address in your browser:

```text
http://127.0.0.1:8000/
```

## 🗄️ Database

The project uses **SQLite** as the default database. Django migrations are used to create and manage the required database tables.

## 🎯 Purpose

The main purpose of this project is to demonstrate the development of a basic web application using Django. It provides practical experience with:

- Django project structure
- Models and database operations
- CRUD functionality
- URL routing
- HTML templates
- Static files
- Git and GitHub

## 🔮 Future Enhancements

The project can be extended with:

- User registration and login
- Librarian and student roles
- Book issue and return functionality
- Due-date and fine calculation
- Book availability tracking
- Advanced search and filtering
- Email notifications
- Improved dashboard and analytics

## 👩‍💻 Project

**Library Management System**

Built as a learning project to practice **Python, Django, database management, web development, and GitHub**.

## 📄 License

This project is created for educational and learning purposes.