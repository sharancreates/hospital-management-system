import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  en: {
    translation: {
      "app_title": "Arogya HMS",
      "login": "Login",
      "register": "Register",
      "forgot_password": "Forgot Password?",
      "dashboard": "Dashboard",
      "appointments": "Appointments",
      "doctors": "Doctors",
      "logout": "Logout",
      "book_appointment": "Book Appointment",
      "upcoming_appointments": "Upcoming Appointments",
      "home_welcome": "Welcome to Arogya Hospital Management System",
      "home_subtitle": "State-of-the-art healthcare management at your fingertips.",
      "patient_portal": "Patient Portal",
      "doctor_portal": "Doctor Portal",
      "admin_portal": "Admin Portal"
    }
  },
  hi: {
    translation: {
      "app_title": "आरोग्य एचएमएस",
      "login": "लॉगिन",
      "register": "पंजीकरण",
      "forgot_password": "पासवर्ड भूल गए?",
      "dashboard": "डैशबोर्ड",
      "appointments": "अपॉइंटमेंट",
      "doctors": "डॉक्टर",
      "logout": "लॉगआउट",
      "book_appointment": "अपॉइंटमेंट बुक करें",
      "upcoming_appointments": "आगामी अपॉइंटमेंट",
      "home_welcome": "आरोग्य अस्पताल प्रबंधन प्रणाली में आपका स्वागत है",
      "home_subtitle": "आपकी उंगलियों पर अत्याधुनिक स्वास्थ्य सेवा प्रबंधन।",
      "patient_portal": "मरीज पोर्टल",
      "doctor_portal": "डॉक्टर पोर्टल",
      "admin_portal": "प्रशासक पोर्टल"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
