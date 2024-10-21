# Jarbuk

**Jarbuk** is a social media web application built to practice and learn the Django framework. The app allows users to create and interact with posts, comment on them, invite friends, like posts/comments, and chat in real-time. Users can also customize their profiles and update login credentials.

> ⚠️ **Note:** This project was created for learning purposes only and is not intended for production use. The Django secret key is visible in the settings file for simplicity. If you plan to use this project, **make sure to replace the secret key** for security reasons.

## Table of Contents
- [Jarbuk](#jarbuk)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Installation and Usage](#installation-and-usage)
    - [Prerequisites](#prerequisites)
    - [Running with Docker](#running-with-docker)
    - [Running without Docker (Optional)](#running-without-docker-optional)
  - [Security Considerations](#security-considerations)
  - [Showcase](#showcase)
  - [License](#license)

## Features

- Create and interact with posts (like, comment, etc.)
- Send and accept friend invitations
- Real-time group and private chat functionality
- Profile management (edit profile, update login credentials)
- Group chat creation
- Notifications for friend requests and message updates

## Tech Stack

- **Backend:** Django
- **Frontend:** HTML, CSS, JavaScript (AJAX for dynamic requests)
- **Real-Time Chat:** Django Channels
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Testing:** Django's built-in testing framework

## Installation and Usage

To get started with Jarbuk, follow the steps below:

### Prerequisites

- Docker and Docker Compose installed on your system.
- Alternatively, Python 3.8+ and Django (if running without Docker).

### Running with Docker

1. Clone the repository:
    ```bash
    git clone https://github.com/mai-kel/Jarbuk.git
    cd jarbuk
    ```

2. Start the application using Docker Compose:
    ```bash
    docker-compose up
    ```

3. The website will be available at:
    ```bash
    http://localhost:8000
    ```

### Running without Docker (Optional)

If you'd prefer to run the application without Docker, follow these steps:

1. Clone the repository and navigate to the project directory.

2. Set up a virtual environment:
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run database migrations:
    ```bash
    python manage.py migrate
    ```

5. Start the development server:
    ```bash
    python manage.py runserver
    ```

6. Open your browser and go to:
    ```bash
    http://localhost:8000
    ```

## Security Considerations

- **Django Secret Key:** Always change the `SECRET_KEY` in the Django settings before running in a production environment.
- **Database:** If using a production-level database, ensure sensitive data such as credentials and keys are stored in environment variables.
- **SSL:** Consider configuring HTTPS in a production environment to secure data in transit.

## Showcase

You can watch a demo of the application in action on YouTube:

[![Jarbuk Showcase](https://img.youtube.com/vi/D9HfPaoUd30/0.jpg)](https://www.youtube.com/watch?v=D9HfPaoUd30)

## License

This project is licensed under the MIT License. See the LICENSE file for details.
