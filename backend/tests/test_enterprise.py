import pytest
import json
from models import Ward, Bed, InpatientAdmission, Nurse, NursingNote, LabOrder, InsurancePolicy, Bill, User
from extensions import db
from datetime import datetime, date

def login_nurse(client, app):
    # Seed nurse user first
    with app.app_context():
        nurse_user = User(
            email='nurse@test.com',
            role='nurse'
        )
        nurse_user.set_password('NursePass123!')
        db.session.add(nurse_user)
        db.session.commit()
        
        nurse_profile = Nurse(
            name='Nurse Nancy',
            contact_num='1112223333',
            user_id=nurse_user.user_id
        )
        db.session.add(nurse_profile)
        db.session.commit()
        
    client.post('/api/v1/auth/login', json={
        'email': 'nurse@test.com',
        'password': 'NursePass123!'
    })

def login_admin(client):
    client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AdminPassword123!'
    })

def login_doctor(client):
    client.post('/api/v1/auth/login', json={
        'email': 'doctor@test.com',
        'password': 'DoctorPassword123!'
    })

def seed_wards_and_beds(app):
    with app.app_context():
        w = Ward(ward_name='ICU-A', ward_type='ICU', capacity=2)
        db.session.add(w)
        db.session.commit()
        
        b1 = Bed(ward_id=w.ward_id, bed_number='ICU-101', status='Available')
        b2 = Bed(ward_id=w.ward_id, bed_number='ICU-102', status='Maintenance')
        db.session.add_all([b1, b2])
        db.session.commit()
        return w.ward_id, b1.bed_id, b2.bed_id

def test_drug_interactions(client, seed_data):
    login_doctor(client)
    # Check interaction between aspirin and warfarin
    res = client.post('/api/v1/enterprise/drug_check', json={
        'drugs': ['aspirin', 'warfarin', 'lisinopril']
    })
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data.get('interaction_found') is True
    assert len(data.get('warnings')) == 1
    assert "High Bleeding Risk" in data.get('warnings')[0]

def test_inpatient_admit_and_discharge_workflow(client, seed_data, app):
    ward_id, b1_id, b2_id = seed_wards_and_beds(app)
    
    # 1. Admit patient using admin user
    login_admin(client)
    res_admit = client.post('/api/v1/enterprise/admit', json={
        'patient_id': seed_data['patient_id'],
        'bed_id': b1_id,
        'reason': 'Patient requires continuous oxygen monitoring.'
    })
    assert res_admit.status_code == 201
    admit_data = json.loads(res_admit.data)
    assert admit_data.get('status') == 'success'
    admission_id = admit_data.get('admission_id')
    
    # Verify bed status changed to Occupied
    with app.app_context():
        bed = Bed.query.get(b1_id)
        assert bed.status == 'Occupied'
        
    # Try admitting to the same occupied bed (should fail)
    res_admit_fail = client.post('/api/v1/enterprise/admit', json={
        'patient_id': seed_data['patient_id'],
        'bed_id': b1_id,
        'reason': 'Duplicate admission.'
    })
    assert res_admit_fail.status_code == 400
    
    # 2. Add nursing note as a nurse
    client.post('/api/v1/auth/logout')
    login_nurse(client, app)
    res_note = client.post('/api/v1/enterprise/nurse/note', json={
        'admission_id': admission_id,
        'note_text': 'Vitals stable. SpO2 at 98% on nasal cannula.'
    })
    assert res_note.status_code == 201
    
    # 3. Discharge patient
    client.post('/api/v1/auth/logout')
    login_doctor(client)
    res_discharge = client.post(f'/api/v1/enterprise/discharge/{admission_id}')
    assert res_discharge.status_code == 200
    
    # Verify bed is available again
    with app.app_context():
        bed = Bed.query.get(b1_id)
        assert bed.status == 'Available'

def test_lab_order_creation(client, seed_data):
    login_doctor(client)
    res = client.post('/api/v1/enterprise/lab/order', json={
        'patient_id': seed_data['patient_id'],
        'doctor_id': seed_data['doctor_id'],
        'test_name': 'Complete Blood Count (CBC)',
        'test_type': 'Blood'
    })
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data.get('status') == 'success'
    assert 'order_id' in data

def test_billing_and_insurance_flow(client, seed_data, app):
    # Set up insurance policy for patient
    with app.app_context():
        policy = InsurancePolicy(
            patient_id=seed_data['patient_id'],
            provider_name='Aetna Healthcare',
            policy_number='POL-998877',
            coverage_limit=150.0
        )
        db.session.add(policy)
        db.session.commit()
        
    login_admin(client)
    
    # Generate bill (Total: 200.0, Insurance limit: 150.0 -> Covered: 150.0, Patient owes: 50.0)
    from services.enterprise_service import generate_bill
    with app.app_context():
        bill = generate_bill(seed_data['patient_id'], 200.0)
        assert bill.insurance_covered == 150.0
        assert bill.status == 'Pending Insurance'
        bill_id = bill.bill_id
        
    # Record patient payment of 50.0
    res_pay = client.post('/api/v1/enterprise/bill/pay', json={
        'bill_id': bill_id,
        'amount': 50.0
    })
    assert res_pay.status_code == 200
    pay_data = json.loads(res_pay.data)
    assert pay_data.get('bill_status') == 'Paid'

def test_export_hl7_and_fhir(client, seed_data):
    login_doctor(client)
    
    # FHIR Export
    res_fhir = client.get(f'/api/v1/enterprise/export/fhir/{seed_data["patient_id"]}')
    assert res_fhir.status_code == 200
    fhir_data = json.loads(res_fhir.data)
    assert fhir_data.get('resourceType') == 'Patient'
    assert fhir_data.get('name')[0].get('text') == 'John Doe'
    
    # HL7 Export
    res_hl7 = client.get(f'/api/v1/enterprise/export/hl7/{seed_data["patient_id"]}')
    assert res_hl7.status_code == 200
    hl7_text = res_hl7.data.decode('utf-8')
    assert 'MSH|^~\\&|HMS' in hl7_text
    assert 'PID|1||' in hl7_text

def test_pharmacy_inventory_and_dispense_flow(client, seed_data, app):
    # 1. Add drug stock as admin
    login_admin(client)
    res_add = client.post('/api/v1/enterprise/pharmacy/add', json={
        'name': 'Paracetamol',
        'quantity': 100,
        'unit': 'tablets',
        'price': 1.5,
        'dosage_form': 'tablet'
    })
    assert res_add.status_code == 201
    
    # 2. Get inventory
    res_get = client.get('/api/v1/enterprise/pharmacy?search=Paracetamol')
    assert res_get.status_code == 200
    get_data = json.loads(res_get.data)
    assert get_data['drugs'][0]['name'] == 'paracetamol'
    assert get_data['drugs'][0]['quantity'] == 100
    
    # 3. Dispense drug as doctor
    client.post('/api/v1/auth/logout')
    login_doctor(client)
    res_disp = client.post('/api/v1/enterprise/pharmacy/dispense', json={
        'name': 'Paracetamol',
        'quantity': 20
    })
    assert res_disp.status_code == 200
    
    # Check remaining stock in DB
    with app.app_context():
        from models import DrugInventory
        drug = DrugInventory.query.filter_by(name='paracetamol').first()
        assert drug.quantity == 80

def test_appointment_reminders(client, seed_data, app):
    # Setup tomorrow appointment
    from datetime import date, timedelta, time
    from models import Appointment
    tomorrow_date = date.today() + timedelta(days=1)
    
    with app.app_context():
        # Create an appointment for tomorrow
        appt = Appointment(
            patient_id=seed_data['patient_id'],
            doctor_id=seed_data['doctor_id'],
            date=tomorrow_date,
            time=time(10, 0),
            token_number=10,
            status="Booked"
        )
        db.session.add(appt)
        db.session.commit()
        
    # Trigger reminder scan
    from services.reminders import check_and_send_appointment_reminders
    with app.app_context():
        res = check_and_send_appointment_reminders()
        assert res['reminders_dispatched'] >= 1
        assert res['date_checked'] == str(tomorrow_date)
