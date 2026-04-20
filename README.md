🌐 **Read this in other language:** [Español](README.es.md)

# 💬 Real-Time Chat Application

## 💼 About This Project

This project is a real-time chat application developed using **Flask** and **Socket.IO**, designed to support multiple users, private messaging, and persistent chat history.

It demonstrates the integration of real-time communication with a scalable backend architecture, combining **MySQL for data persistence**, **Redis for message brokering and session management**, and **Nginx as a reverse proxy**.

The system is fully containerized using Docker, enabling consistent deployment and service orchestration.

---

## 📌 Overview

The application allows users to:

* Join a shared chat environment
* Send and receive real-time messages
* Initiate private conversations
* Persist chat history in a database

---

## 🏗️ Architecture

```
             +-----------------+
             |     NGINX       |
             |    (Port 80)    |
             +--------+--------+
                      |
               Proxy to port 5000
                      |
             +--------v--------+
             |      Web        |
             | Flask + Socket  |
             |  (Port 5000)    |
             +--------+--------+
                      |
          +-----------+------------+
          |                        |
  +-------v------+         +-------v------+
  |    MySQL     |         |    Redis     |
  |  (Port 3306) |         |  (Port 6379) |
  +--------------+         +--------------+
```

---

## ⚙️ System Components

### 🌐 Nginx

* Acts as a reverse proxy
* Routes HTTP and WebSocket traffic to the Flask application

### 🧠 Flask + Socket.IO

* Handles HTTP routes (login, chat, history)
* Manages real-time communication between clients
* Runs on port 5000 inside the container

### 🗄️ MySQL

* Stores users and chat messages
* Ensures persistent data storage

### ⚡ Redis

* Manages user sessions
* Acts as a Pub/Sub broker for Socket.IO
* Enables scalable real-time communication

---

## 🧩 Services

* **web**: Flask application with Socket.IO
* **mysql**: Database initialized with `init.sql`
* **redis**: Cache and message broker
* **nginx**: Reverse proxy

All services run within a shared Docker network.

---

## 🚀 Features

* Real-time messaging using WebSockets
* Private and public chat support
* Persistent chat history
* Multi-user environment
* Scalable architecture with Redis Pub/Sub
* Containerized setup with Docker Compose

---

## 🛠️ Tech Stack

**Backend**

* Python (Flask)
* Flask-SocketIO

**Infrastructure**

* Docker / Docker Compose
* Nginx

**Database & Cache**

* MySQL
* Redis

---

## ⚙️ Installation & Setup

### 🔧 Requirements

* Docker
* Docker Compose

---

### 📥 Installation

Clone the repository:

```bash
git clone https://github.com/StefiVergini/chat-StefaniaVergini.git
cd chat-StefaniaVergini
```

---

### ▶️ Run the application

```bash
docker-compose up --build
```

---

### 🌐 Access

Open your browser and go to:

```
http://localhost
```

---

## 🔐 Usage

* Enter a username and password
* If the user does not exist, it will be created automatically
* Once logged in, you can:

  * View connected users
  * Send public messages
  * Start private chats

---

## 💡 Architecture Highlights

* Separation of concerns using microservices
* Real-time communication handled via WebSockets
* Redis used for horizontal scalability and session handling
* Reverse proxy setup with Nginx
* Fully containerized environment

---

## 📈 Future Improvements

* User authentication enhancements (JWT)
* Message delivery status (read/unread)
* File sharing support
* UI/UX improvements

---

## 👩‍💻 Author

**Stefanía Vergini**
Full-Stack Developer

---

## 📬 Contact

Open to new opportunities and collaborations
