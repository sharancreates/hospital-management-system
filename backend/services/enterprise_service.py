from extensions import db
from models import (
    Ward, Bed, InpatientAdmission, Nurse, NursingNote, 
    LabOrder, InsurancePolicy, Bill, Referral, Patient, User, Doctor, DrugInventory
)
from services.audit_service import log_audit
from datetime import datetime
import json

INTERACTION_DATABASE = {
    ("aspirin", "warfarin"): "High Bleeding Risk - Avoid concurrent administration.",
    ("ibuprofen", "aspirin"): "Increased Risk of GI Bleeding - Monitor closely.",
    ("lisinopril", "spironolactone"): "Risk of Hyperkalemia - Monitor potassium levels."
}

def check_drug_interactions(drugs):
    """
    Checks list of drugs for known hazardous combinations.
    """
    warnings = []
    normalized = [d.strip().lower() for d in drugs if d]
    for i in range(len(normalized)):
        for j in range(i + 1, len(normalized)):
            pair1 = (normalized[i], normalized[j])
            pair2 = (normalized[j], normalized[i])
            if pair1 in INTERACTION_DATABASE:
                warnings.append(INTERACTION_DATABASE[pair1])
            elif pair2 in INTERACTION_DATABASE:
                warnings.append(INTERACTION_DATABASE[pair2])
    return warnings

def admit_patient(patient_id, bed_id, reason):
    bed = Bed.query.get_or_404(bed_id)
    if bed.status != 'Available':
        raise ValueError(f"Bed {bed.bed_number} is not available (Status: {bed.status})")
    
    admission = InpatientAdmission(
        patient_id=patient_id,
        bed_id=bed_id,
        reason=reason
    )
    bed.status = 'Occupied'
    db.session.add(admission)
    db.session.commit()
    
    log_audit("INPATIENT_ADMIT", "InpatientAdmission", admission.admission_id, {
        "patient_id": patient_id,
        "bed_id": bed_id
    })
    return admission

def discharge_patient(admission_id):
    admission = InpatientAdmission.query.get_or_404(admission_id)
    if admission.discharged_at is not None:
        raise ValueError("Patient already discharged")
        
    admission.discharged_at = datetime.utcnow()
    admission.bed.status = 'Available'
    db.session.commit()
    
    log_audit("INPATIENT_DISCHARGE", "InpatientAdmission", admission.admission_id)
    return admission

def add_nursing_note(admission_id, user_id, note_text):
    nurse = Nurse.query.filter_by(user_id=user_id).first()
    if not nurse:
        raise ValueError("User is not registered as a nurse")
        
    note = NursingNote(
        admission_id=admission_id,
        nurse_id=nurse.nurse_id,
        note_text=note_text
    )
    db.session.add(note)
    db.session.commit()
    
    log_audit("CREATE_NURSING_NOTE", "NursingNote", note.note_id)
    return note

def create_lab_order(patient_id, doctor_id, test_name, test_type):
    order = LabOrder(
        patient_id=patient_id,
        doctor_id=doctor_id,
        test_name=test_name,
        test_type=test_type
    )
    db.session.add(order)
    db.session.commit()
    
    log_audit("CREATE_LAB_ORDER", "LabOrder", order.order_id, {
        "test_name": test_name,
        "test_type": test_type
    })
    return order

def add_insurance_policy(patient_id, provider_name, policy_number, coverage_limit):
    policy = InsurancePolicy(
        patient_id=patient_id,
        provider_name=provider_name,
        policy_number=policy_number,
        coverage_limit=coverage_limit
    )
    db.session.add(policy)
    db.session.commit()
    
    log_audit("ADD_INSURANCE_POLICY", "InsurancePolicy", policy.policy_id)
    return policy

def generate_bill(patient_id, total_amount, appointment_id=None, admission_id=None):
    # Lookup insurance
    policy = InsurancePolicy.query.filter_by(patient_id=patient_id).first()
    insurance_covered = 0.0
    if policy:
        insurance_covered = min(float(total_amount), float(policy.coverage_limit))
        
    bill = Bill(
        patient_id=patient_id,
        appointment_id=appointment_id,
        admission_id=admission_id,
        total_amount=total_amount,
        insurance_covered=insurance_covered,
        paid_amount=0.0,
        status='Pending Insurance' if insurance_covered > 0 else 'Unpaid'
    )
    db.session.add(bill)
    db.session.commit()
    
    log_audit("GENERATE_BILL", "Bill", bill.bill_id, {
        "total_amount": total_amount,
        "insurance_covered": insurance_covered
    })
    return bill

def record_payment(bill_id, payment_amount):
    bill = Bill.query.get_or_404(bill_id)
    bill.paid_amount += float(payment_amount)
    
    remaining = bill.total_amount - bill.insurance_covered - bill.paid_amount
    if remaining <= 0:
        bill.status = 'Paid'
    else:
        bill.status = 'Partial'
        
    db.session.commit()
    log_audit("RECORD_PAYMENT", "Bill", bill.bill_id, {"payment_amount": payment_amount})
    return bill

def export_patient_fhir(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    log_audit("EXPORT_FHIR", "Patient", patient_id)
    
    fhir_data = {
        "resourceType": "Patient",
        "id": str(patient.patient_id),
        "active": True,
        "name": [
            {
                "use": "official",
                "text": patient.pat_name
            }
        ],
        "gender": patient.gender.lower() if patient.gender else "unknown",
        "birthDate": str(patient.dob),
        "telecom": [
            {
                "system": "phone",
                "value": patient.contact_num,
                "use": "mobile"
            }
        ]
    }
    return fhir_data

def export_patient_hl7(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    log_audit("EXPORT_HL7", "Patient", patient_id)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Generate simple HL7 v2 Message segment lines
    msh = f"MSH|^~\\&|HMS|HMSFAC|RECEIVING|RECEIVINGFAC|{timestamp}||ADT^A08|MSG00001|P|2.3|||"
    pid = f"PID|1||{patient.patient_id}^^^MR||{patient.pat_name}||{patient.dob.strftime('%Y%m%d') if patient.dob else ''}|{patient.gender[:1] if patient.gender else 'U'}|||||{patient.contact_num}|||||"
    
    return f"{msh}\r{pid}"

def get_drug_inventory(page=1, per_page=10, search_query=None):
    query = DrugInventory.query
    if search_query:
        query = query.filter(DrugInventory.name.ilike(f"%{search_query}%"))
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "drugs": [{
            "drug_id": d.drug_id,
            "name": d.name,
            "quantity": d.quantity,
            "unit": d.unit,
            "price": d.price,
            "dosage_form": d.dosage_form
        } for d in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages
    }

def add_drug_stock(name, quantity, unit, price, dosage_form):
    normalized_name = name.strip().lower()
    drug = DrugInventory.query.filter_by(name=normalized_name).first()
    if drug:
        drug.quantity += int(quantity)
        drug.price = float(price)
        drug.unit = unit
        drug.dosage_form = dosage_form
    else:
        drug = DrugInventory(
            name=normalized_name,
            quantity=int(quantity),
            unit=unit,
            price=float(price),
            dosage_form=dosage_form
        )
        db.session.add(drug)
        
    db.session.commit()
    log_audit("PHARMACY_STOCK_ADD", "DrugInventory", drug.drug_id, {
        "name": normalized_name,
        "added_quantity": quantity,
        "total_quantity": drug.quantity
    })
    return drug

def dispense_drug(name, quantity):
    normalized_name = name.strip().lower()
    drug = DrugInventory.query.filter_by(name=normalized_name).first()
    if not drug:
        raise ValueError(f"Drug '{name}' not found in inventory")
    if drug.quantity < int(quantity):
        raise ValueError(f"Insufficient stock for '{name}'. Available: {drug.quantity}, Requested: {quantity}")
        
    drug.quantity -= int(quantity)
    db.session.commit()
    log_audit("PHARMACY_DISPENSE", "DrugInventory", drug.drug_id, {
        "name": normalized_name,
        "dispensed_quantity": quantity,
        "remaining_quantity": drug.quantity
    })
    return drug
