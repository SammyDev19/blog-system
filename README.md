# Blog System

A full-stack blog application built with Python and Flask.

The application allows users to create accounts, publish and manage blog posts, interact with posts through likes and comments, search for posts, and manage their profiles. It also includes an administrator dashboard for managing users and posts.

## Features

- User registration and login
- Secure password hashing
- Session-based authentication
- Create, edit and delete posts
- Like and unlike posts
- Comment on posts
- Search posts
- User profiles
- Account deletion
- Admin dashboard
- Admin user management
- Admin post management
- SQLite database
- Responsive dark-themed interface

## Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- Bootstrap
- Jinja2
- Werkzeug
- python-dotenv

## Installation

1. Clone the repository:

git clone https://github.com/SammyCruz19/blog-system.git

2. Navigate into the project:

cd blog-system

3. Create a virtual environment:

python -m venv venv

4. Activate the virtual environment on Windows:

venv\Scripts\activate

5. Install the dependencies:

pip install -r requirements.txt

6. Create a `.env` file in the project folder and add:

SECRET_KEY=your-secret-key

7. Run the application:

python app.py

8. Open the local address shown in the terminal in your browser.

## Project Structure

blog-system/
│
├── app.py
├── database.py
├── models.py
├── blog.db
├── requirements.txt
├── .gitignore
├── README.md
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── post.html
│   ├── create_post.html
│   ├── edit_post.html
│   └── admin.html
│
└── static/
    └── style.css

## Author

Samuel Ogbolu