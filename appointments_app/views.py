from django.db import connection
from activity_logger import log_activity
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.http import JsonResponse

# Helpers
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def validate_id(id):
    try:
        id = int(id)
        return id if id > 0 else None
    except:
        return None

#   ADD/BOOK APPOINTMENT
def book_appointment(request):
    def api_error(message, status=400):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': message}, status=status)
        return render(request, "appointments_app/add_appointment.html", {"error": message})

    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor_id')
        date = request.POST.get('date')
        fee = request.POST.get('fee', '0') or '0'
        status = request.POST.get('status')

        if not patient_id or not doctor_id or not date:
            return api_error("All fields are required")
        
        if not fee.isdigit():
            fee = '0'
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM PATIENTS WHERE PATIENT_ID = %s",[patient_id])
            if not cursor.fetchone():
                return api_error("Invalid patient")
            cursor.execute("SELECT * FROM DOCTORS WHERE DOCTOR_ID=%s", [doctor_id])
            if not cursor.fetchone():
                return api_error("Invalid doctor")
            
            cursor.execute("""
                           INSERT INTO APPOINTMENT (APPOINTMENT_DATE,CONSULTATION_FEE,APPOINTMENT_STATUS,
                           PATIENT_ID,DOCTOR_ID)
                           VALUES (%s,%s,%s,%s,%s)
                           """,[date,fee,status,patient_id,doctor_id])

        log_activity(f"Patient:{patient_id}", "Appointment scheduled", f"Date:{date}, Doctor:{doctor_id}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("appointments_list")
    return render(request,"index.html")

#   DELETE APPOINTMENT
def delete_appointment(request,id):
    id = validate_id(id)

    if not id:
        return render(request, "error.html", {"error": "Invalid ID"})
    
    log_activity("Admin", "Appointment cancelled", f"Appointment ID:{id}")
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM APPOINTMENT WHERE APPOINTMENT_ID = %s", [id])

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect("appointments_list")

#   GET APPOINTMENT
def get_appointment(request,id):
    id = validate_id(id)

    if not id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid ID'}, status=400)
        return render(request,"error.html",{"error":"Invalid ID"})
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM APPOINTMENT WHERE APPOINTMENT_ID = %s",[id])
        data = dictfetchall(cursor)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data[0] if data else {}, safe=False)

    return render(request,"appointments_app/edit_appointment.html",{"appointment":data[0] if data else None})

#   UPDATE APPOINTMENT
def update_appoitnment(request,id):
    id = validate_id(id)

    if not id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid ID'}, status=400)
        return render(request,"error.html",{"error":"Invalid ID"})
    
    if request.method == "POST":
        def api_error(message, status=400):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': message}, status=status)
            return render(request,"appointments_app/edit_appointment.html",{"error": message})

        date = request.POST.get("date")
        fee = request.POST.get("fee", "0") or "0"
        status = request.POST.get("status")

        if not date or not status:
            return api_error("All fields are required")
        
        if not fee.isdigit():
            fee = "0"
        
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE APPOINTMENT
                           SET APPOINTMENT_DATE = %s,CONSULTATION_FEE=%s,APPOINTMENT_STATUS=%s
                           WHERE APPOINTMENT_ID = %s
                           """,[date,fee,status,id])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("appointments_list")
    
    return redirect("appointments_list")

def appointments_json(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT A.APPOINTMENT_ID, A.PATIENT_ID, A.DOCTOR_ID, A.APPOINTMENT_DATE,
                       A.APPOINTMENT_STATUS, A.CONSULTATION_FEE, P.PATIENT_NAME, D.DOCTOR_NAME
                       FROM APPOINTMENT A 
                       JOIN PATIENTS P ON A.PATIENT_ID = P.PATIENT_ID
                       JOIN DOCTORS D ON A.DOCTOR_ID = D.DOCTOR_ID
                       ORDER BY A.APPOINTMENT_DATE DESC
                       """)
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False)


def appointments_today_json(request):
    from datetime import date
    today = date.today()
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT A.APPOINTMENT_ID, A.PATIENT_ID, A.DOCTOR_ID, A.APPOINTMENT_DATE,
                       A.APPOINTMENT_STATUS, A.CONSULTATION_FEE, P.PATIENT_NAME, D.DOCTOR_NAME
                       FROM APPOINTMENT A 
                       JOIN PATIENTS P ON A.PATIENT_ID = P.PATIENT_ID
                       JOIN DOCTORS D ON A.DOCTOR_ID = D.DOCTOR_ID
                       WHERE DATE(A.APPOINTMENT_DATE) = %s
                       ORDER BY A.APPOINTMENT_DATE ASC
                       """, [today])
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False)