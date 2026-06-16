from django.db import connection
from django.http import JsonResponse
from datetime import date


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def safe_count(cursor, query, params=None):
    try:
        cursor.execute(query, params or [])
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception:
        return 0


def stats_json(request):
    today = date.today()

    with connection.cursor() as cursor:
        total_patients     = safe_count(cursor, "SELECT COUNT(*) FROM PATIENTS")
        total_doctors      = safe_count(cursor, "SELECT COUNT(*) FROM DOCTORS")
        today_appointments = safe_count(cursor,
            "SELECT COUNT(*) FROM APPOINTMENT WHERE DATE(APPOINTMENT_DATE) = %s", [today])
        today_tests        = safe_count(cursor,
            "SELECT COUNT(*) FROM TEST_RECORDS WHERE DATE(TEST_DATE) = %s", [today])
        total_bills        = safe_count(cursor, "SELECT COUNT(*) FROM BILLS")  

    return JsonResponse({
        "patients":     total_patients,
        "doctors":      total_doctors,
        "appointments": today_appointments,
        "today_tests":  today_tests,
        "bills":        total_bills,   
    })


def logs_json(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT username, action, details, logged_at
                FROM ACTIVITY_LOG
                ORDER BY logged_at DESC
                LIMIT 20
            """)
            logs = dictfetchall(cursor)
        return JsonResponse(logs, safe=False)

    except Exception:
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT P.PATIENT_NAME AS username, 'Patient added' AS action,
                           NULL AS details, P.CREATED_AT AS logged_at
                    FROM PATIENTS P
                    UNION ALL
                    SELECT D.DOCTOR_NAME, 'Doctor added', NULL, D.CREATED_AT
                    FROM DOCTORS D
                    UNION ALL
                    SELECT P.PATIENT_NAME, 'Appointment scheduled', NULL, A.CREATED_AT
                    FROM APPOINTMENT A JOIN PATIENTS P ON A.PATIENT_ID = P.PATIENT_ID
                    UNION ALL
                    SELECT P.PATIENT_NAME, 'Test record created', NULL, TR.CREATED_AT
                    FROM TEST_RECORDS TR JOIN PATIENTS P ON TR.PATIENT_ID = P.PATIENT_ID
                    ORDER BY logged_at DESC
                    LIMIT 20
                """)
                logs = dictfetchall(cursor)
            return JsonResponse(logs, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)