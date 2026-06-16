from django.db import connection, transaction
from django.http import JsonResponse
from activity_logger import log_activity

#   Helpers
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def validate_id(value):
    try:
        pk = int(value)
        return pk if pk > 0 else None
    except (TypeError, ValueError):
        return None


#   Bills List 
def bills_json(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    B.BILL_ID, B.PATIENT_ID, P.PATIENT_NAME,
                    B.CONSULTATION_FEE, B.TEST_FEE,
                    B.TOTAL_AMOUNT, B.PAYMENT_STATUS, B.BILL_DATE
                FROM BILLS B
                JOIN PATIENTS P ON B.PATIENT_ID = P.PATIENT_ID
                ORDER BY B.BILL_DATE DESC
            """)
            data = dictfetchall(cursor)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#   Bills Stats
def bills_stats(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM BILLS")
            total_bills = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(TOTAL_AMOUNT) FROM BILLS")
            total_amount = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(TOTAL_AMOUNT) FROM BILLS WHERE PAYMENT_STATUS = 'Paid'")
            received = cursor.fetchone()[0] or 0

        return JsonResponse({
            "total_bills":  total_bills,
            "total_revenue": float(total_amount),
            "received":     float(received),
            "pending":      float(total_amount - received),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Add Bill
def add_bill(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    patient_id = validate_id(request.POST.get("patient_id"))
    if not patient_id:
        return JsonResponse({"error": "Valid patient required"}, status=400)

    try:
        consultation_fee = float(request.POST.get("consultation_fee") or 0)
        test_fee         = float(request.POST.get("test_fee") or 0)
        total_amount     = consultation_fee + test_fee
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid fee amount"}, status=400)

    payment_status = request.POST.get("payment_status", "Pending")
    if payment_status not in ("Pending", "Paid", "Partial"):
        payment_status = "Pending"

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT PATIENT_NAME FROM PATIENTS WHERE PATIENT_ID = %s",
                    [patient_id]
                )
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({"error": "Patient not found"}, status=400)

                cursor.execute("""
                    INSERT INTO BILLS
                        (PATIENT_ID, CONSULTATION_FEE, TEST_FEE, TOTAL_AMOUNT, PAYMENT_STATUS)
                    VALUES (%s, %s, %s, %s, %s)
                """, [patient_id, consultation_fee, test_fee, total_amount, payment_status])

        log_activity(row[0], "Bill generated", f"Total: {total_amount}")
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#   Mark Bill Paid
def mark_bill_paid(request, bill_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    bill_id = validate_id(bill_id)
    if not bill_id:
        return JsonResponse({"error": "Invalid ID"}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM BILLS WHERE BILL_ID = %s", [bill_id])
            if not cursor.fetchone():
                return JsonResponse({"error": "Bill not found"}, status=404)

            cursor.execute(
                "UPDATE BILLS SET PAYMENT_STATUS = 'Paid' WHERE BILL_ID = %s",
                [bill_id]
            )
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#   Delete Bill

def delete_bill(request, bill_id):
    if request.method not in ("GET", "POST"):
        return JsonResponse({"error": "Invalid method"}, status=405)

    bill_id = validate_id(bill_id)
    if not bill_id:
        return JsonResponse({"error": "Invalid ID"}, status=400)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM BILLS WHERE BILL_ID = %s", [bill_id])
            if not cursor.fetchone():
                return JsonResponse({"error": "Bill not found"}, status=404)

            cursor.execute("DELETE FROM BILLS WHERE BILL_ID = %s", [bill_id])
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)