from datetime import datetime, date, timedelta
from extensions import db
from models import Appointment, Patient, Doctor
from flask import current_app

def check_and_send_appointment_reminders():
    """
    Scans for booked appointments scheduled for the next day (tomorrow) 
    and dispatches simulated reminders to logs.
    """
    tomorrow = date.today() + timedelta(days=1)
    
    # Query all active/booked appointments scheduled for tomorrow
    upcoming_appointments = Appointment.query.filter_by(
        date=tomorrow,
        status="Booked"
    ).all()
    
    reminders_sent = 0
    
    for appt in upcoming_appointments:
        patient = appt.patient
        doctor = appt.doctor
        
        if not patient or not doctor:
            continue
            
        # Compile notification payloads
        patient_email = patient.user.email if patient.user else "N/A"
        patient_phone = patient.contact_num
        message = (
            f"Dear {patient.pat_name}, this is a reminder for your upcoming appointment "
            f"with Dr. {doctor.doc_name} scheduled tomorrow on {appt.date} at {appt.time.strftime('%I:%M %p')}. "
            f"Your booking token number is {appt.token_number}."
        )
        
        # Log simulated SMS & Email dispatch logs
        current_app.logger.info(f"[SMS Reminder dispatched to {patient_phone}]: {message}")
        current_app.logger.info(f"[Email Reminder dispatched to {patient_email}]: {message}")
        
        reminders_sent += 1
        
    return {
        "status": "success",
        "reminders_dispatched": reminders_sent,
        "date_checked": str(tomorrow)
    }

def start_reminder_daemon(app):
    """
    Optionally run daemon thread in background to dispatch reminders periodically
    """
    import threading
    import time
    
    def run_poll():
        app.logger.info("Initializing appointment reminders daemon listener thread...")
        while True:
            try:
                with app.app_context():
                    res = check_and_send_appointment_reminders()
                    app.logger.info(f"Reminders check cycle ran: {res}")
            except Exception as e:
                try:
                    with app.app_context():
                        db.session.rollback()
                except Exception:
                    pass
                app.logger.error(f"Error in reminders daemon loop: {str(e)}")
            finally:
                try:
                    with app.app_context():
                        db.session.remove()
                except Exception:
                    pass
            
            # Check once every 12 hours (43200 seconds)
            time.sleep(43200)

    thread = threading.Thread(target=run_poll, daemon=True)
    thread.start()
