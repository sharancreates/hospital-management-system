from app import create_app
from extensions import db
from models import User, Department
from werkzeug.security import generate_password_hash

def create_admin():
    admin_email = 'arogya@xyz.com'
    admin_password = 'arogya1@2'

    existing_admin = User.query.filter_by(email = admin_email).first()

    if not existing_admin:
        admin_user = User(email = admin_email, password_hash = generate_password_hash(admin_password), role = 'admin')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created.")
    else:
        print("Admin already exists.")

def depts():
    departments = [
    ('Cardiology', 'Heart and Circulatory System'),
    ('Neurology', 'Nervous System and Brain'),
    ('Immunology', 'Allergy Specialist'),
    ('Dermatology', 'Skin and Hair'),
    ('Gastroenterology', 'Digestive System'),
    ('Endocrinology', 'Hormones and Metabolism'),
    ('Pulmonology', 'Lungs and Respiratory System'),
    ('Nephrology', 'Kidney Disorders'),
    ('Hematology', 'Blood Disorders'),
    ('Oncology', 'Cancer Diagnosis and Treatment'),
    ('Rheumatology', 'Joints and Autoimmune Disorders'),
    ('Ophthalmology', 'Eye and Vision Care'),
    ('Otolaryngology', 'Ear, Nose, and Throat'),
    ('Orthopedics', 'Bones, Joints, and Muscles'),
    ('Urology', 'Urinary Tract and Male Reproductive System'),
    ('Gynecology', 'Female Reproductive Health'),
    ('Obstetrics', 'Pregnancy and Childbirth'),
    ('Pediatrics', 'Child and Adolescent Health'),
    ('Geriatrics', 'Elderly Health Care'),
    ('Psychiatry', 'Mental Health and Disorders'),
    ('Psychology', 'Behavior and Cognitive Health'),
    ('Anesthesiology', 'Anesthesia and Pain Management'),
    ('Pathology', 'Disease Diagnosis via Lab Testing'),
    ('Radiology', 'Medical Imaging'),
    ('Nuclear Medicine', 'Radioactive Diagnostics and Therapy'),
    ('Infectious Disease', 'Infections and Contagious Illnesses'),
    ('Plastic Surgery', 'Reconstructive and Cosmetic Surgery'),
    ('Sports Medicine', 'Sports Injuries and Performance'),
    ('Emergency Medicine', 'Acute Care and Trauma'),
    ('Palliative Care', 'End-of-Life and Chronic Illness Support')
    ]

    for name, d in departments:
        exists = Department.query.filter_by(department_name = name).first()
        if not exists:
            new_dept = Department(department_name = name, description = d)
            db.session.add(new_dept)
            db.session.commit()
            print("Department added : ", name)
        else:
            print("Department already present.")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        create_admin()
        depts()        
