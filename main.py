from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import math

app = FastAPI()

# -----------------------------
# Initial Data
# -----------------------------
doctors = [
    {"id": 1, "name": "Dr. A", "specialization": "Cardiologist", "fee": 500, "experience_years": 10, "is_available": True},
    {"id": 2, "name": "Dr. B", "specialization": "Dermatologist", "fee": 300, "experience_years": 5, "is_available": True},
    {"id": 3, "name": "Dr. C", "specialization": "Pediatrician", "fee": 400, "experience_years": 8, "is_available": False},
    {"id": 4, "name": "Dr. D", "specialization": "General", "fee": 200, "experience_years": 3, "is_available": True},
    {"id": 5, "name": "Dr. E", "specialization": "Cardiologist", "fee": 600, "experience_years": 15, "is_available": True},
    {"id": 6, "name": "Dr. F", "specialization": "General", "fee": 250, "experience_years": 6, "is_available": False},
]

appointments = []
appt_counter = 1

# -----------------------------
# Models
# -----------------------------
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False

class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True

# -----------------------------
# Helpers
# -----------------------------
def find_doctor(doctor_id):
    for d in doctors:
        if d["id"] == doctor_id:
            return d
    return None

def calculate_fee(base_fee, appointment_type, senior=False):
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee

    original_fee = fee

    if senior:
        fee = fee * 0.85

    return int(original_fee), int(fee)

def filter_doctors_logic(specialization, max_fee, min_exp, is_available):
    result = doctors
    if specialization is not None:
        result = [d for d in result if d["specialization"] == specialization]
    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]
    if min_exp is not None:
        result = [d for d in result if d["experience_years"] >= min_exp]
    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    return result

# -----------------------------
# Basic Routes (Q1–5)
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}

@app.get("/doctors")
def get_doctors():
    return {
        "doctors": doctors,
        "total": len(doctors),
        "available_count": sum(d["is_available"] for d in doctors)
    }

@app.get("/doctors/summary")
def doctors_summary():
    return {
        "total": len(doctors),
        "available": sum(d["is_available"] for d in doctors),
        "most_experienced": max(doctors, key=lambda x: x["experience_years"])["name"],
        "cheapest_fee": min(d["fee"] for d in doctors),
        "specialization_count": {
            s: sum(d["specialization"] == s for d in doctors)
            for s in set(d["specialization"] for d in doctors)
        }
    }

@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    return filter_doctors_logic(specialization, max_fee, min_experience, is_available)



@app.get("/appointments")
def get_appointments():
    return {"appointments": appointments, "total": len(appointments)}

# -----------------------------
# POST + Filters (Q6–10)
# -----------------------------
@app.post("/appointments")
def create_appointment(req: AppointmentRequest):
    global appt_counter

    doc = find_doctor(req.doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")

    if not doc["is_available"]:
        raise HTTPException(400, "Doctor not available")

    original_fee, final_fee = calculate_fee(doc["fee"], req.appointment_type, req.senior_citizen)

    appt = {
        "appointment_id": appt_counter,
        "patient": req.patient_name,
        "doctor": doc["name"],
        "doctor_id": doc["id"],
        "date": req.date,
        "type": req.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appt)
    appt_counter += 1
    doc["is_available"] = False

    return appt



# -----------------------------
# CRUD (Q11–15)
# -----------------------------
@app.post("/doctors", status_code=201)
def add_doctor(new_doc: NewDoctor):
    if any(d["name"] == new_doc.name for d in doctors):
        raise HTTPException(400, "Doctor already exists")

    doc = new_doc.dict()
    doc["id"] = len(doctors) + 1
    doctors.append(doc)
    return doc

@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: Optional[int] = None, is_available: Optional[bool] = None):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Not found")

    if fee is not None:
        doc["fee"] = fee
    if is_available is not None:
        doc["is_available"] = is_available

    return doc

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Not found")

    for a in appointments:
        if a["doctor_id"] == doctor_id and a["status"] == "scheduled":
            raise HTTPException(400, "Doctor has active appointments")

    doctors.remove(doc)
    return {"message": "Deleted"}

@app.post("/appointments/{appointment_id}/confirm")
def confirm_appt(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "confirmed"
            return a
    raise HTTPException(404, "Not found")

@app.post("/appointments/{appointment_id}/cancel")
def cancel_appt(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "cancelled"
            doc = find_doctor(a["doctor_id"])
            if doc:
                doc["is_available"] = True
            return a
    raise HTTPException(404, "Not found")

@app.post("/appointments/{appointment_id}/complete")
def complete_appt(appointment_id: int):
    for a in appointments:
        if a["appointment_id"] == appointment_id:
            a["status"] = "completed"
            return a
    raise HTTPException(404, "Not found")

@app.get("/appointments/active")
def active_appts():
    return [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]

@app.get("/appointments/by-doctor/{doctor_id}")
def appts_by_doc(doctor_id: int):
    return [a for a in appointments if a["doctor_id"] == doctor_id]

# -----------------------------
# Advanced (Q16–20)
# -----------------------------
@app.get("/doctors/search")
def search_doctors(keyword: str):
    res = [d for d in doctors if keyword.lower() in d["name"].lower() or keyword.lower() in d["specialization"].lower()]
    if not res:
        return {"message": "No doctors found"}
    return {"results": res, "total_found": len(res)}

@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee"):
    if sort_by not in ["fee", "name", "experience_years"]:
        raise HTTPException(400, "Invalid sort field")
    return sorted(doctors, key=lambda x: x[sort_by])

@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    total = len(doctors)
    total_pages = math.ceil(total / limit)
    start = (page - 1) * limit
    return {
        "data": doctors[start:start + limit],
        "total_pages": total_pages
    }

@app.get("/appointments/search")
def search_appts(name: str):
    return [a for a in appointments if name.lower() in a["patient"].lower()]

@app.get("/appointments/sort")
def sort_appts(sort_by: str = "date"):
    return sorted(appointments, key=lambda x: x.get(sort_by, ""))

@app.get("/appointments/page")
def paginate_appts(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    return appointments[start:start + limit]

@app.get("/doctors/browse")
def browse(
    keyword: Optional[str] = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = doctors

    if keyword:
        result = [d for d in result if keyword.lower() in d["name"].lower()]

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    return {
        "data": result[start:start + limit],
        "total": len(result)
    }

@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    doc = find_doctor(doctor_id)
    if not doc:
        raise HTTPException(404, "Doctor not found")
    return doc
