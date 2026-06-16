from django.db import connection
from activity_logger import log_activity
from django.shortcuts import render, redirect
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

#   ADD DOCTOR
def add_doctor(request):
    def api_error(message, status=400):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': message}, status=status)
        return render(request, "doctors_app/add_doctor.html", {"error": message})

    if request.method == "POST":
        name = request.POST.get('name')
        specialization = request.POST.get('specialization')
        user_id = request.POST.get('user_id')

        if not name or not specialization:
            return api_error("All fields are required")
        
        if user_id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM USERS WHERE USER_ID = %s",[user_id])
                if not cursor.fetchone():
                    return api_error("Invalid user")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO DOCTORS (DOCTOR_NAME, SPECIALIZATION, USER_ID)
                VALUES (%s, %s, %s)
            """, [name, specialization, user_id if user_id else None])

        log_activity(name, "Doctor added", f"Specialization:{specialization}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("doctors_list")
    
    return render(request,"index.html")

#   DELETE DOCTOR
def delete_doctor(request,id):
    id = validate_id(id)
    if not id:
        return render(request,"error.html",{"error": "Invalid ID"})
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DOCTOR_NAME FROM DOCTORS WHERE DOCTOR_ID = %s", [id])
        row = cursor.fetchone()
        dname = row[0] if row else f'ID:{id}'
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM DOCTORS WHERE DOCTOR_ID = %s", [id])
    log_activity(dname, "Doctor deleted", f"Doctor ID:{id}")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect("doctors_list")

#   UPDATE DOCTOR
def update_doctor(request,id):
    id = validate_id(id)

    if not id:
        return render(request, "error.html", {"error": "Invalid ID"})

    if request.method == "POST":
        def api_error(message, status=400):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': message}, status=status)
            return render(request, "doctors_app/edit_doctor.html", {"error": message})

        name = request.POST.get("name")
        specialization = request.POST.get("specialization")
        user_id = request.POST.get("user_id")

        if not name or not specialization:
            return api_error("All fields required")
        
        if user_id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM USERS WHERE USER_ID = %s", [user_id])
                if not cursor.fetchone():
                    return api_error("Invalid user")
                
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE DOCTORS
                           SET DOCTOR_NAME =%s,
                           SPECIALIZATION = %s,
                           USER_ID = %s
                           WHERE DOCTOR_ID = %s
                           """,[name,specialization,user_id,id])

        log_activity(name, "Doctor updated", f"ID:{id}, Spec:{specialization}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("doctors_list")

    return redirect("doctors_list")

def doctors_json(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM DOCTORS ORDER BY DOCTOR_ID DESC")
        data = dictfetchall(cursor)

    return JsonResponse(data, safe=False)