# Jarbuk

**Jarbuk** is a social media web application built to practice and learn the Django framework. The app allows users to create and interact with posts, comment on them, invite friends, like posts/comments, and chat in real-time. Users can also customize their profiles and update login credentials.

> ⚠️ **Note:** This project was created for learning purposes only and is not intended for production use. The Django secret key is visible in the settings file for simplicity. If you plan to use this project, **make sure to replace the secret key** for security reasons.

## Features

- Create and interact with posts 
- Send and accept friend invitations
- Real-time group and private chat functionality
- Profile management (edit profile, update login credentials)
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

## Showcase

You can watch a demo of the application in action on YouTube:

[![Jarbuk Showcase](https://img.youtube.com/vi/D9HfPaoUd30/0.jpg)](https://www.youtube.com/watch?v=D9HfPaoUd30)

## License

This project is licensed under the MIT License. See the LICENSE file for details.
