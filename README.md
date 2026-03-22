🏥 FastAPI Medical Appointment System

📌 Project Description

This project is a backend system built using FastAPI for managing medical appointments efficiently.
It allows users to manage doctors, schedule appointments, track consultations, and handle hospital workflows.

---

🚀 Features

- Home route
- Get all doctors
- Get doctor by ID
- Get appointments
- Doctors summary
- Create appointment
- Field validation using Pydantic
- Filter doctors by specialization, fee, availability
- Add new doctor
- Update doctor details
- Delete doctor
- Appointment → Check-in → Check-out
- Active appointments tracking
- Search doctors
- Sort doctors
- Pagination
- Combined browse API

---

🛠 Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic

---

▶️ How to Run the Project

1. Install dependencies

pip install -r requirements.txt

2. Run the server

uvicorn main:app --reload

3. Open in browser

http://127.0.0.1:8000/docs

---

📂 Project Structure

Medical-Appointment-System/
│── screenshots/
│── README.md
│── main.py
│── requirements.txt

---

📌 API Testing

All APIs can be tested using Swagger UI:
👉 http://127.0.0.1:8000/docs

---

📖 About FastAPI

FastAPI is a modern, high-performance Python web framework used for building APIs quickly with automatic validation and documentation.

---

👩‍💻 Author

Shreya G
