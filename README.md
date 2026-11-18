# BlogPost – Django Blog Management System

A web-based blog management application developed using Python and Django. It allows users to create, manage, explore, and interact with blog posts through a user-friendly interface.

## Features

- User Registration and Login
- Create, Read, Update and Delete (CRUD) Blog Posts
- Category and Tag Management
- Search Blog Posts
- Filter Posts by Category and Author
- AI-Powered Blog Summarization
- Guest Access to Search, Filtering and AI Summarization
- Responsive User Interface

## Technologies Used

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** SQLite
- **AI Integration:** AI-based text summarization

## Project Structure

```text
BlogPost/
├── blog/
├── posts/
├── users/
├── templates/
├── static/
├── manage.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd BlogPost
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Open your browser and visit:

http://127.0.0.1:8000/

## Future Enhancements

- Multilingual Support
- Improved Accessibility
- Enhanced Security
- Performance Optimization

## Developer

Developed as part of an MCA academic project.