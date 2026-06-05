from app import create_app 
from extensions import db
from models import User, Doctor, Patient, Department, Appointment, Treatment, Availability
from werkzeug.security import generate_password_hash
from datetime import date, time, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        print("WARNING: This will clear all existing data. Press Ctrl+C to cancel within 3 seconds.")
        
        # 1. Clean Slate (delete data but preserve schema & alembic_version)
        print("Clearing tables...")
        db.session.query(Treatment).delete()
        db.session.query(Appointment).delete()
        db.session.query(Availability).delete()
        db.session.query(Patient).delete()
        db.session.query(Doctor).delete()
        db.session.query(User).delete()
        db.session.query(Department).delete()
        db.session.commit()
        print("--- Database Cleared ---")

        # 2. Create Departments
        dept_names = [
            ('Cardiology', 'Heart and cardiovascular system care'),
            ('Neurology', 'Brain and nervous system disorders'),
            ('Pediatrics', 'Medical care for infants, children, and adolescents'),
            ('Orthopedics', 'Musculoskeletal system care'),
            ('Dermatology', 'Skin, hair, and nail conditions'),
            ('General Medicine', 'Primary healthcare and general checkups')
        ]
        
        departments = []
        for name, desc in dept_names:
            d = Department(department_name=name, description=desc)
            departments.append(d)
        
        db.session.add_all(departments)
        db.session.commit() # Commit to generate IDs
        print("--- Departments Created ---")

        import os
        # 3. Create Admin User
        admin_email = os.environ.get('ADMIN_EMAIL') or 'admin@arogya.com'
        admin_password = os.environ.get('ADMIN_PASSWORD') or 'admin123'
        admin_user = User(
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role='admin'
        )
        db.session.add(admin_user)
        print(f"--- Admin Created ({admin_email}) ---")

        # 4. Create Doctors (User + Doctor Profile)
        doctor_data = [
            ("Dr. Sarah Smith", "female", "Cardiology"),
            ("Dr. Rahul Jain", "male", "Neurology"),
            ("Dr. Anjali Patel", "female", "Pediatrics"),
            ("Dr. Vikram Singh", "male", "Orthopedics"),
            ("Dr. Emily Davis", "female", "Dermatology")
        ]

        doctors_objs = []

        for i, (name, gender, dept_name) in enumerate(doctor_data):
            # A. Create User Account
            email = f"doc{i+1}@arogya.com"
            user = User(
                email=email,
                password_hash=generate_password_hash('doc123'),
                role='doctor'
            )
            db.session.add(user)
            db.session.flush() # Flush to get user.user_id

            # B. Find Department
            dept = next(d for d in departments if d.department_name == dept_name)

            # C. Create Doctor Profile linked to User and Dept
            doc = Doctor(
                doc_name=name,
                gender=gender,
                dob=date(1980, 5, 15),
                contact_num=f"98765432{i}0",
                user_id=user.user_id,
                department_id=dept.department_id 
            )
            db.session.add(doc)
            doctors_objs.append(doc)

        print("--- Doctors Created (doc1@arogya.com to doc5@arogya.com / doc123) ---")

        # 5. Create Patients (User + Patient Profile)
        patient_data = [
            ("Rajesh Kumar", "male", 45),
            ("Sunita Sharma", "female", 32),
            ("Amit Verma", "male", 28)
        ]

        patients_objs = []

        for i, (name, gender, age) in enumerate(patient_data):
            # A. Create User Account
            email = f"pat{i+1}@gmail.com"
            user = User(
                email=email,
                password_hash=generate_password_hash('pat123'),
                role='patient'
            )
            db.session.add(user)
            db.session.flush()

            # B. Create Patient Profile (age computed dynamically from dob)
            pat = Patient(
                pat_name=name,
                gender=gender,
                contact_num=f"99887766{i}5",
                dob=date(date.today().year - age, 1, 1), 
                user_id=user.user_id
            )
            db.session.add(pat)
            patients_objs.append(pat)

        print("--- Patients Created (pat1@gmail.com / pat123) ---")
        
        db.session.commit() # Commit all doctors and patients

        # 6. Add Availability for Doctors
        availabilities = []
        today = date.today()
        
        for doc in doctors_objs:
            availabilities.append(Availability(
                doctor_id=doc.doctor_id,
                date=today,
                start_time=time(10, 0),
                end_time=time(11, 0)
            ))
            availabilities.append(Availability(
                doctor_id=doc.doctor_id,
                date=today + timedelta(days=1),
                start_time=time(14, 0),
                end_time=time(15, 0)
            ))
        
        db.session.add_all(availabilities)
        print("--- Availability Slots Created ---")

        # 7. Create Dummy Appointments & Treatments
        completed_appt = Appointment(
            patient_id=patients_objs[0].patient_id, # Rajesh
            doctor_id=doctors_objs[0].doctor_id,    # Dr. Sarah
            date=today - timedelta(days=5),         # 5 days ago
            time=time(10, 0),
            token_number=101,
            status='Completed'
        )
        db.session.add(completed_appt)
        db.session.flush()

        treatment = Treatment(
            ailment="Hypertension",
            prescription="Tab Amlodipine 5mg OD\nTab Aspirin 75mg OD",
            notes="Patient advised to reduce salt intake and walk daily.",
            appointment_id=completed_appt.appointment_id,
            date=completed_appt.date
        )
        db.session.add(treatment)

        booked_appt = Appointment(
            patient_id=patients_objs[1].patient_id, # Sunita
            doctor_id=doctors_objs[2].doctor_id,    # Dr. Anjali (Pediatrics)
            date=today + timedelta(days=1),         # Tomorrow
            time=time(14, 0),
            token_number=202,
            status='Booked'
        )
        db.session.add(booked_appt)

        db.session.commit()
        print("--- Appointments & Treatments Created ---")
        print("--- SUCCESS: Database Populated ---")

def auto_seed_database_if_empty(app):
    from models import User, Doctor, Patient, Department, Appointment, Treatment, Availability
    with app.app_context():
        db.create_all()
        if User.query.first() is not None:
            app.logger.warning("Database already initialized and contains data. Skipping auto-seed.")
            return

        app.logger.warning("No users found in database. Initiating auto-seed...")
        
        # 1. Create Departments
        dept_names = [
            ('Cardiology', 'Heart and cardiovascular system care'),
            ('Neurology', 'Brain and nervous system disorders'),
            ('Pediatrics', 'Medical care for infants, children, and adolescents'),
            ('Orthopedics', 'Musculoskeletal system care'),
            ('Dermatology', 'Skin, hair, and nail conditions'),
            ('General Medicine', 'Primary healthcare and general checkups')
        ]
        
        departments = []
        for name, desc in dept_names:
            d = Department(department_name=name, description=desc)
            departments.append(d)
        
        db.session.add_all(departments)
        db.session.commit()

        import os
        # 2. Create Admin User
        admin_email = os.environ.get('ADMIN_EMAIL') or 'admin@arogya.com'
        admin_password = os.environ.get('ADMIN_PASSWORD') or 'admin123'
        admin_user = User(
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role='admin'
        )
        db.session.add(admin_user)

        # 3. Create Doctors
        doctor_data = [
            ("Dr. Sarah Smith", "female", "Cardiology"),
            ("Dr. Rahul Jain", "male", "Neurology"),
            ("Dr. Anjali Patel", "female", "Pediatrics"),
            ("Dr. Vikram Singh", "male", "Orthopedics"),
            ("Dr. Emily Davis", "female", "Dermatology")
        ]

        doctors_objs = []
        for i, (name, gender, dept_name) in enumerate(doctor_data):
            email = f"doc{i+1}@arogya.com"
            user = User(
                email=email,
                password_hash=generate_password_hash('doc123'),
                role='doctor'
            )
            db.session.add(user)
            db.session.flush()

            dept = next(d for d in departments if d.department_name == dept_name)
            doc = Doctor(
                doc_name=name,
                gender=gender,
                dob=date(1980, 5, 15),
                contact_num=f"98765432{i}0",
                user_id=user.user_id,
                department_id=dept.department_id 
            )
            db.session.add(doc)
            doctors_objs.append(doc)

        # 4. Create Patients
        patient_data = [
            ("Rajesh Kumar", "male", 45),
            ("Sunita Sharma", "female", 32),
            ("Amit Verma", "male", 28)
        ]

        patients_objs = []
        for i, (name, gender, age) in enumerate(patient_data):
            email = f"pat{i+1}@gmail.com"
            user = User(
                email=email,
                password_hash=generate_password_hash('pat123'),
                role='patient'
            )
            db.session.add(user)
            db.session.flush()

            pat = Patient(
                pat_name=name,
                gender=gender,
                contact_num=f"99887766{i}5",
                dob=date(date.today().year - age, 1, 1), 
                user_id=user.user_id
            )
            db.session.add(pat)
            patients_objs.append(pat)

        db.session.commit()

        # 5. Add Availability for Doctors
        availabilities = []
        today = date.today()
        for doc in doctors_objs:
            availabilities.append(Availability(
                doctor_id=doc.doctor_id,
                date=today,
                start_time=time(10, 0),
                end_time=time(11, 0)
            ))
            availabilities.append(Availability(
                doctor_id=doc.doctor_id,
                date=today + timedelta(days=1),
                start_time=time(14, 0),
                end_time=time(15, 0)
            ))
        db.session.add_all(availabilities)

        # 6. Create Dummy Appointments & Treatments
        completed_appt = Appointment(
            patient_id=patients_objs[0].patient_id,
            doctor_id=doctors_objs[0].doctor_id,
            date=today - timedelta(days=5),
            time=time(10, 0),
            token_number=101,
            status='Completed'
        )
        db.session.add(completed_appt)
        db.session.flush()

        treatment = Treatment(
            ailment="Hypertension",
            prescription="Tab Amlodipine 5mg OD\nTab Aspirin 75mg OD",
            notes="Patient advised to reduce salt intake and walk daily.",
            appointment_id=completed_appt.appointment_id,
            date=completed_appt.date
        )
        db.session.add(treatment)

        booked_appt = Appointment(
            patient_id=patients_objs[1].patient_id,
            doctor_id=doctors_objs[2].doctor_id,
            date=today + timedelta(days=1),
            time=time(14, 0),
            token_number=202,
            status='Booked'
        )
        db.session.add(booked_appt)

        db.session.commit()
        app.logger.warning("Database automatically seeded successfully!")

if __name__ == '__main__':
    seed_database()