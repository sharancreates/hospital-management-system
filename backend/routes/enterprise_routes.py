from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from routes.utils import role_required, sanitize_string
from models import Ward, Bed, InpatientAdmission, LabOrder, Bill
from extensions import db, limiter
from services import enterprise_service

enterprise_bp = Blueprint('enterprise', __name__, url_prefix='/api/v1/enterprise')

@enterprise_bp.route('/wards', methods=['GET'])
@login_required
def get_wards():
    wards = Ward.query.all()
    if not wards:
        w1 = Ward(ward_name='General Ward A', ward_type='General Ward', capacity=4)
        w2 = Ward(ward_name='Intensive Care Unit (ICU)', ward_type='ICU', capacity=2)
        w3 = Ward(ward_name='Semi-Private Wing', ward_type='Semi-Private', capacity=2)
        db.session.add_all([w1, w2, w3])
        db.session.flush()
        
        for i in range(1, 5):
            db.session.add(Bed(ward_id=w1.ward_id, bed_number=f"GW-A{i}", status='Available'))
        for i in range(1, 3):
            db.session.add(Bed(ward_id=w2.ward_id, bed_number=f"ICU-{i}", status='Available'))
        for i in range(1, 3):
            db.session.add(Bed(ward_id=w3.ward_id, bed_number=f"SP-{i}", status='Available'))
            
        db.session.commit()
        wards = Ward.query.all()

    data = []
    for w in wards:
        beds_data = []
        for b in w.beds:
            active_admission = next((adm for adm in b.admissions if adm.discharged_at is None), None)
            beds_data.append({
                "bed_id": b.bed_id,
                "bed_number": b.bed_number,
                "status": b.status,
                "active_admission": {
                    "admission_id": active_admission.admission_id,
                    "patient_id": active_admission.patient_id,
                    "patient_name": active_admission.patient.pat_name,
                    "admitted_at": active_admission.admitted_at.isoformat(),
                    "reason": active_admission.reason
                } if active_admission else None
            })
        data.append({
            "ward_id": w.ward_id,
            "ward_name": w.ward_name,
            "ward_type": w.ward_type,
            "capacity": w.capacity,
            "beds": beds_data
        })
    return jsonify({"status": "success", "wards": data})

@enterprise_bp.route('/admit', methods=['POST'])
@role_required('admin', 'doctor')
def admit():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    patient_id = data.get('patient_id')
    bed_id = data.get('bed_id')
    reason = sanitize_string(data.get('reason', ''), min_len=2, max_len=500, field_name="Admission Reason")
    
    if not (patient_id and bed_id and reason):
        return jsonify({"message": "Missing required fields", "status": "error"}), 400
        
    try:
        admission = enterprise_service.admit_patient(patient_id, bed_id, reason)
        return jsonify({
            "message": "Patient admitted successfully",
            "admission_id": admission.admission_id,
            "status": "success"
        }), 201
    except ValueError as e:
        return jsonify({"message": str(e), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error during admission: {str(e)}")
        return jsonify({"message": f"Database error: {str(e)}", "status": "error"}), 500

@enterprise_bp.route('/discharge/<int:admission_id>', methods=['POST'])
@role_required('admin', 'doctor')
def discharge(admission_id):
    try:
        enterprise_service.discharge_patient(admission_id)
        return jsonify({"message": "Patient discharged successfully", "status": "success"})
    except ValueError as e:
        return jsonify({"message": str(e), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error during discharge: {str(e)}")
        return jsonify({"message": f"Database error: {str(e)}", "status": "error"}), 500

@enterprise_bp.route('/nurse/note', methods=['POST'])
@role_required('nurse', 'admin')
def add_note():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    admission_id = data.get('admission_id')
    note_text = sanitize_string(data.get('note_text', ''), min_len=2, max_len=1000, field_name="Nursing Note")
    
    if not (admission_id and note_text):
        return jsonify({"message": "Missing fields", "status": "error"}), 400
        
    try:
        note = enterprise_service.add_nursing_note(admission_id, current_user.user_id, note_text)
        return jsonify({
            "message": "Note added successfully",
            "note_id": note.note_id,
            "status": "success"
        }), 201
    except ValueError as e:
        return jsonify({"message": str(e), "status": "error"}), 400
    except Exception as e:
        current_app.logger.error(f"Error adding nursing note: {str(e)}")
        return jsonify({"message": f"Database error: {str(e)}", "status": "error"}), 500

@enterprise_bp.route('/lab/order', methods=['POST'])
@role_required('doctor', 'admin')
def create_lab_order():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    patient_id = data.get('patient_id')
    doctor_id = data.get('doctor_id')
    test_name = sanitize_string(data.get('test_name', ''), min_len=2, max_len=100, field_name="Test Name")
    test_type = sanitize_string(data.get('test_type', ''), min_len=2, max_len=50, field_name="Test Type")
    
    if not (patient_id and doctor_id and test_name and test_type):
        return jsonify({"message": "Missing fields", "status": "error"}), 400
        
    try:
        order = enterprise_service.create_lab_order(patient_id, doctor_id, test_name, test_type)
        return jsonify({
            "message": "Lab order created successfully",
            "order_id": order.order_id,
            "status": "success"
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error creating lab order: {str(e)}")
        return jsonify({"message": f"Database error: {str(e)}", "status": "error"}), 500

@enterprise_bp.route('/bill/pay', methods=['POST'])
@role_required('admin')
def pay_bill():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    bill_id = data.get('bill_id')
    amount = data.get('amount')
    
    if not (bill_id and amount):
        return jsonify({"message": "Missing fields", "status": "error"}), 400
        
    try:
        bill = enterprise_service.record_payment(bill_id, amount)
        return jsonify({
            "message": "Payment recorded successfully",
            "status": "success",
            "paid_amount": bill.paid_amount,
            "bill_status": bill.status
        })
    except Exception as e:
        current_app.logger.error(f"Error paying bill: {str(e)}")
        return jsonify({"message": f"Database error: {str(e)}", "status": "error"}), 500

@enterprise_bp.route('/drug_check', methods=['POST'])
@role_required('doctor', 'admin')
def drug_check():
    data = request.get_json()
    if not data or 'drugs' not in data:
        return jsonify({"message": "List of drugs is required", "status": "error"}), 400
        
    drugs = data.get('drugs')
    warnings = enterprise_service.check_drug_interactions(drugs)
    return jsonify({
        "status": "success",
        "warnings": warnings,
        "interaction_found": len(warnings) > 0
    })

@enterprise_bp.route('/export/fhir/<int:patient_id>', methods=['GET'])
@role_required('admin', 'doctor')
def export_fhir(patient_id):
    try:
        fhir_data = enterprise_service.export_patient_fhir(patient_id)
        return jsonify(fhir_data)
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@enterprise_bp.route('/export/hl7/<int:patient_id>', methods=['GET'])
@role_required('admin', 'doctor')
def export_hl7(patient_id):
    try:
        hl7_data = enterprise_service.export_patient_hl7(patient_id)
        # Return HL7 as plain text standard payload
        return hl7_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@enterprise_bp.route('/pharmacy', methods=['GET'])
@role_required('admin', 'doctor', 'nurse')
def get_pharmacy_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', None, type=str)
    
    inventory = enterprise_service.get_drug_inventory(page, per_page, search)
    return jsonify({"status": "success", **inventory})

@enterprise_bp.route('/pharmacy/add', methods=['POST'])
@role_required('admin')
def add_pharmacy_stock():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    name = sanitize_string(data.get('name', ''), min_len=2, max_len=100, field_name="Drug Name")
    quantity = data.get('quantity')
    unit = sanitize_string(data.get('unit', ''), min_len=1, max_len=20, field_name="Unit")
    price = data.get('price')
    dosage_form = sanitize_string(data.get('dosage_form', ''), min_len=2, max_len=50, field_name="Dosage Form")
    
    if not (name and quantity is not None and unit and price is not None and dosage_form):
        return jsonify({"message": "Missing required fields", "status": "error"}), 400
        
    try:
        drug = enterprise_service.add_drug_stock(name, quantity, unit, price, dosage_form)
        return jsonify({
            "message": "Stock updated successfully",
            "drug_id": drug.drug_id,
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@enterprise_bp.route('/pharmacy/dispense', methods=['POST'])
@role_required('admin', 'doctor')
def dispense_pharmacy_drug():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    name = sanitize_string(data.get('name', ''), min_len=2, max_len=100, field_name="Drug Name")
    quantity = data.get('quantity')
    
    if not (name and quantity):
        return jsonify({"message": "Missing fields", "status": "error"}), 400
        
    try:
        enterprise_service.dispense_drug(name, quantity)
        return jsonify({"message": "Drug dispensed successfully", "status": "success"})
    except ValueError as e:
        return jsonify({"message": str(e), "status": "error"}), 400
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@enterprise_bp.route('/bills', methods=['GET'])
@role_required('admin')
def get_bills():
    bills = Bill.query.all()
    data = []
    for b in bills:
        data.append({
            "bill_id": b.bill_id,
            "patient_id": b.patient_id,
            "patient_name": b.patient.pat_name,
            "total_amount": b.total_amount,
            "insurance_covered": b.insurance_covered,
            "paid_amount": b.paid_amount,
            "status": b.status,
            "created_at": b.created_at.isoformat()
        })
    return jsonify({"status": "success", "bills": data})

@enterprise_bp.route('/bill/generate', methods=['POST'])
@role_required('admin')
def create_bill():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    patient_id = data.get('patient_id')
    total_amount = data.get('total_amount')
    appointment_id = data.get('appointment_id')
    admission_id = data.get('admission_id')
    
    if not (patient_id and total_amount):
        return jsonify({"message": "Patient ID and Total Amount are required", "status": "error"}), 400
        
    try:
        bill = enterprise_service.generate_bill(patient_id, total_amount, appointment_id, admission_id)
        return jsonify({
            "message": "Bill generated successfully",
            "bill_id": bill.bill_id,
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@enterprise_bp.route('/insurance/add', methods=['POST'])
@role_required('admin')
def add_insurance():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid data", "status": "error"}), 400
        
    patient_id = data.get('patient_id')
    provider_name = sanitize_string(data.get('provider_name', ''), min_len=2, max_len=100, field_name="Provider Name")
    policy_number = sanitize_string(data.get('policy_number', ''), min_len=2, max_len=100, field_name="Policy Number")
    coverage_limit = data.get('coverage_limit')
    
    if not (patient_id and provider_name and policy_number and coverage_limit is not None):
        return jsonify({"message": "Missing required fields", "status": "error"}), 400
        
    try:
        policy = enterprise_service.add_insurance_policy(patient_id, provider_name, policy_number, coverage_limit)
        return jsonify({
            "message": "Insurance policy registered successfully",
            "policy_id": policy.policy_id,
            "status": "success"
        }), 201
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500
