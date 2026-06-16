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

# HOME
def home(request):
    return render(request, "index.html")

# ADD PATIENTS
def add_patient(request):
    def api_error(message, status=400):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': message}, status=status)
        return render(request, 'index.html', {'error': message})

    if request.method == "POST":
        name = request.POST.get("name")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        blood = request.POST.get("blood")

        if not name or not age or not gender or not blood:
            return api_error("All fields required")

        if not age.isdigit():
            return api_error("Age must be numeric")

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO PATIENTS (PATIENT_NAME, PATIENT_AGE, PATIENT_GENDER, PATIENT_BLOOD_GROUP)
                VALUES (%s, %s, %s, %s)
            """, [name, int(age), gender, blood])
        log_activity(name, "Patient added", f"Name:{name}, Age:{age}, Gender:{gender}")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("patients")
    return render(request, "index.html")

#   DELETE PATIENT

def del_patient(request, id):
    id = validate_id(id)
    if not id:
        return render(request, "error.html", {"error": "Invalid ID"})

    with connection.cursor() as cursor:
        cursor.execute("SELECT PATIENT_NAME FROM PATIENTS WHERE PATIENT_ID = %s", [id])
        row = cursor.fetchone()
        pname = row[0] if row else f'ID:{id}'
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM PATIENTS WHERE PATIENT_ID = %s", [id])
    log_activity(pname, "Patient deleted", f"Patient ID:{id}")
    # if ajax, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect("patients")

#   UPDATE PATIENT
def update_patient(request, id):
    id = validate_id(id)
    if not id:
        return render(request, "error.html", {"error": "Invalid ID"})

    if request.method == "POST":
        def api_error(message, status=400):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': message}, status=status)
            return render(request, 'edit_patient.html', {'error': message})

        name = request.POST.get("name")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        blood = request.POST.get("blood")

        if not name or not age or not gender or not blood:
            return api_error("All fields required")

        if not age.isdigit():
            return api_error("Age must be numeric")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PATIENTS
                SET PATIENT_NAME=%s,
                    PATIENT_AGE=%s,
                    PATIENT_GENDER=%s,
                    PATIENT_BLOOD_GROUP=%s
                WHERE PATIENT_ID=%s
            """, [name, int(age), gender, blood, id])

        log_activity(name, "Patient updated", f"ID:{id}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect("patients")

    return redirect("patients")

def patients_json(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PATIENTS ORDER BY CREATED_AT DESC")
        data = dictfetchall(cursor)

    return JsonResponse(data, safe=False)