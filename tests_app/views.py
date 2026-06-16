from django.db import connection
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


# ADD TEST RECORD
def add_test_record(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == "POST":

        patient_id = request.POST.get("patient_id")
        doctor_id = request.POST.get("doctor_id")
        lab_id = request.POST.get("lab_id")
        test_id   = request.POST.get("test_id")      
        test_name = request.POST.get("test_name")    
        date = request.POST.get("date")
        status = request.POST.get("status")
        result = request.POST.get("result")

        allowed_status = ["PENDING", "INCOMPLETE", "COMPLETED"]
        allowed_result = ["POSITIVE", "NEGATIVE", "INCONCLUSIVE", "NOT DONE"]

        if not patient_id or not doctor_id or not (test_id or test_name) or not date:
            if is_ajax:
                return JsonResponse({"error": "All fields are required"}, status=400)
            return render(request, "add_test.html", {
                "error": "All fields are required"
            })

        if status not in allowed_status:
            if is_ajax:
                return JsonResponse({"error": "Invalid status"}, status=400)
            return render(request, "add_test.html", {
                "error": "Invalid status"
            })

        if result not in allowed_result:
            if is_ajax:
                return JsonResponse({"error": "Invalid result"}, status=400)
            return render(request, "add_test.html", {
                "error": "Invalid result"
            })

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT 1 FROM PATIENTS WHERE PATIENT_ID = %s",
                [patient_id]
            )

            if not cursor.fetchone():
                if is_ajax:
                    return JsonResponse({"error": "Invalid patient"}, status=400)
                return render(request, "add_test.html", {
                    "error": "Invalid patient"
                })

            cursor.execute(
                "SELECT 1 FROM DOCTORS WHERE DOCTOR_ID = %s",
                [doctor_id]
            )

            if not cursor.fetchone():
                if is_ajax:
                    return JsonResponse({"error": "Invalid doctor"}, status=400)
                return render(request, "add_test.html", {
                    "error": "Invalid doctor"
                })

            cursor.execute(
                "SELECT 1 FROM LABORATORY WHERE LAB_ID = %s",
                [lab_id]
            )

            if not cursor.fetchone():
                if is_ajax:
                    return JsonResponse({"error": "Invalid lab"}, status=400)
                return render(request, "add_test.html", {
                    "error": "Invalid lab"
                })

            if test_id:
                cursor.execute("SELECT TEST_ID, TEST_NAME FROM TESTS WHERE TEST_ID = %s", [test_id])
                row = cursor.fetchone()
                if not row:
                    if is_ajax:
                        return JsonResponse({"error": "Invalid test selected"}, status=400)
                test_name = row[1] if row else test_name
            else:
                cursor.execute(
                    "SELECT TEST_ID FROM TESTS WHERE TEST_NAME = %s AND LAB_ID = %s",
                    [test_name, lab_id]
                )
                existing_test = cursor.fetchone()
                if existing_test:
                    test_id = existing_test[0]
                else:
                    cursor.execute("""
                        INSERT INTO TESTS (TEST_NAME, TEST_FEE, LAB_ID)
                        VALUES (%s, %s, %s)
                    """, [test_name, 0, lab_id])
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    test_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO TEST_RECORDS
                (TEST_DATE, TEST_STATUS, TEST_RESULT,
                 PATIENT_ID, DOCTOR_ID, TEST_ID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [date, status, result,
                  patient_id, doctor_id, test_id])

        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS ACTIVITY_LOG (ID INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, action TEXT, details TEXT, logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                cursor.execute("SELECT PATIENT_NAME FROM PATIENTS WHERE PATIENT_ID = %s", [patient_id])
                pname = cursor.fetchone()[0] if cursor.fetchone() is not None else ''
                cursor.execute("INSERT INTO ACTIVITY_LOG (username, action, details) VALUES (%s, %s, %s)", [pname or '', 'Test record created', f'{test_name}'])
        except Exception:
            pass

        if is_ajax:
            return JsonResponse({"success": True})
        return redirect("test_records")

    return render(request, "add_test.html")


# DELETE RECORD
def delete_record(request, id):

    id = validate_id(id)

    if not id:
        return render(request, "error.html", {
            "error": "Invalid ID"
        })

    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM TEST_RECORDS WHERE RECORD_ID = %s",
            [id]
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True})
    return redirect("test_records")


# GET RECORD
def get_record(request, id):

    id = validate_id(id)

    if not id:
        return render(request, "error.html", {
            "error": "Invalid ID"
        })

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT *
            FROM TEST_RECORDS
            WHERE RECORD_ID = %s
        """, [id])

        data = dictfetchall(cursor)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data[0] if data else {}, safe=False)

    return render(request, "edit_test.html", {
        "record": data[0] if data else None
    })


# UPDATE RECORD
def update_record(request, id):

    id = validate_id(id)

    if not id:
        return render(request, "error.html", {
            "error": "Invalid ID"
        })

    if request.method == "POST":

        date = request.POST.get("date")
        status = request.POST.get("status")
        result = request.POST.get("result")

        allowed_status = ["PENDING", "INCOMPLETE", "COMPLETED"]

        allowed_result = [
            "POSITIVE",
            "NEGATIVE",
            "INCONCLUSIVE",
            "NOT DONE"
        ]

        if not date:
            return render(request, "edit_test.html", {
                "error": "Date required"
            })

        if status not in allowed_status:
            return render(request, "edit_test.html", {
                "error": "Invalid status"
            })

        if result not in allowed_result:
            return render(request, "edit_test.html", {
                "error": "Invalid result"
            })

        with connection.cursor() as cursor:

            cursor.execute("""
                UPDATE TEST_RECORDS
                SET
                    TEST_DATE = %s,
                    TEST_STATUS = %s,
                    TEST_RESULT = %s
                WHERE RECORD_ID = %s
            """, [date, status, result, id])

        # if ajax, respond with JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True})

        return redirect("test_records")

    return redirect("test_records")


# ADD TEST
def add_test(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == "POST":

        test_name = (request.POST.get("test_name") or "").strip()
        test_fee = request.POST.get("test_fee", 0)
        lab_id = request.POST.get("lab_id")

        if not test_name or not lab_id:
            if is_ajax:
                return JsonResponse({"error": "Test name and lab are required"}, status=400)
            return render(request, "add_test.html", {"error": "All fields are required"})

        try:
            test_fee = float(test_fee) if test_fee else 0.0
            if test_fee < 0:
                if is_ajax:
                    return JsonResponse({"error": "Fee cannot be negative"}, status=400)
                return render(request, "add_test.html", {"error": "Fee cannot be negative"})
        except ValueError:
            if is_ajax:
                return JsonResponse({"error": "Invalid fee"}, status=400)
            return render(request, "add_test.html", {"error": "Invalid fee"})

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM LABORATORY WHERE LAB_ID = %s", [lab_id])
                if not cursor.fetchone():
                    if is_ajax:
                        return JsonResponse({"error": "Invalid Lab"}, status=400)
                    return render(request, "add_test.html", {"error": "Invalid Lab"})

                cursor.execute("""
                    INSERT INTO TESTS (TEST_NAME, TEST_FEE, LAB_ID)
                    VALUES (%s, %s, %s)
                """, [test_name, test_fee, lab_id])

            if is_ajax:
                return JsonResponse({"success": True})
            return redirect("list_test")
        except Exception as e:
            if is_ajax:
                return JsonResponse({"error": str(e)}, status=500)
            return render(request, "add_test.html", {"error": str(e)})

    return render(request, "add_test.html")


# DELETE TEST
def delete_test(request, id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    id = validate_id(id)
    if not id:
        if is_ajax:
            return JsonResponse({"error": "Invalid ID"}, status=400)
        return render(request, "error.html", {"error": "Invalid ID"})
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM TESTS WHERE TEST_ID = %s", [id])
        if is_ajax:
            return JsonResponse({"success": True})
        return redirect("list_test")
    except Exception as e:
        if is_ajax:
            return JsonResponse({"error": str(e)}, status=500)
        return redirect("list_test")


# GET TEST
def get_test(request, id):
    id = validate_id(id)
    if not id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"error": "Invalid ID"}, status=400)
        return render(request, "error.html", {"error": "Invalid ID"})

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT T.TEST_ID, T.TEST_NAME, T.TEST_FEE, T.LAB_ID, L.LAB_NAME
            FROM TESTS T
            LEFT JOIN LABORATORY L ON T.LAB_ID = L.LAB_ID
            WHERE T.TEST_ID = %s
        """, [id])
        data = dictfetchall(cursor)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(data[0] if data else {}, safe=False)
    return render(request, "edit_test.html", {"test": data[0] if data else None})


# UPDATE TEST
def update_test(request, id):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    id = validate_id(id)

    if not id:
        if is_ajax:
            return JsonResponse({"error": "Invalid ID"}, status=400)
        return render(request, "error.html", {"error": "Invalid ID"})

    if request.method == "POST":

        test_name = (request.POST.get("test_name") or "").strip()
        test_fee = request.POST.get("test_fee", 0)
        lab_id = request.POST.get("lab_id")

        if not test_name or not lab_id:
            if is_ajax:
                return JsonResponse({"error": "Test name and lab are required"}, status=400)
            return render(request, "edit_test.html", {"error": "All fields are required"})

        try:
            test_fee = float(test_fee) if test_fee else 0.0
            if test_fee < 0:
                if is_ajax:
                    return JsonResponse({"error": "Fee cannot be negative"}, status=400)
                return render(request, "edit_test.html", {"error": "Fee cannot be negative"})
        except ValueError:
            if is_ajax:
                return JsonResponse({"error": "Invalid fee"}, status=400)
            return render(request, "edit_test.html", {"error": "Invalid fee"})

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM LABORATORY WHERE LAB_ID = %s", [lab_id])
                if not cursor.fetchone():
                    if is_ajax:
                        return JsonResponse({"error": "Invalid Lab"}, status=400)
                    return render(request, "edit_test.html", {"error": "Invalid Lab"})

                cursor.execute("""
                    UPDATE TESTS
                    SET TEST_NAME = %s, TEST_FEE = %s, LAB_ID = %s
                    WHERE TEST_ID = %s
                """, [test_name, test_fee, lab_id, id])

            if is_ajax:
                return JsonResponse({"success": True})
            return redirect("list_test")
        except Exception as e:
            if is_ajax:
                return JsonResponse({"error": str(e)}, status=500)
            return redirect("list_test")

    if is_ajax:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    return redirect("list_test")


def tests_json(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT T.TEST_ID, T.TEST_NAME, T.TEST_FEE, T.LAB_ID,
                   COALESCE(L.LAB_NAME, '') as LAB_NAME
            FROM TESTS T
            LEFT JOIN LABORATORY L ON T.LAB_ID = L.LAB_ID
            ORDER BY T.TEST_NAME ASC
        """)
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False)

def records_json(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                TR.RECORD_ID,
                TR.PATIENT_ID,
                TR.DOCTOR_ID,
                TR.TEST_ID,
                TR.TEST_DATE,
                TR.TEST_STATUS,
                TR.TEST_RESULT,
                P.PATIENT_NAME,
                D.DOCTOR_NAME,
                T.TEST_NAME,
                L.LAB_NAME,
                P.PATIENT_BLOOD_GROUP as blood_group
            FROM TEST_RECORDS TR
            JOIN PATIENTS P ON TR.PATIENT_ID = P.PATIENT_ID
            JOIN DOCTORS D ON TR.DOCTOR_ID = D.DOCTOR_ID
            JOIN TESTS T ON TR.TEST_ID = T.TEST_ID
            JOIN LABORATORY L ON T.LAB_ID = L.LAB_ID
            ORDER BY TR.TEST_DATE DESC
        """)
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False)