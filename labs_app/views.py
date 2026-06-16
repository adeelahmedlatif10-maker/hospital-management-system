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

def list_lab(request):

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT *
            FROM LABORATORY
            ORDER BY LAB_ID DESC
        """)

        labs = dictfetchall(cursor)

    return render(request, "labs.html", {
        "labs": labs
    })


# ADD LAB
def add_lab(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == "POST":

        lab_name = request.POST.get("lab_name")

        if not lab_name:
            if is_ajax:
                return JsonResponse({"error": "Lab name required"}, status=400)
            return render(request, "add_lab.html", {
                "error": "Lab name required"
            })

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT 1
                FROM LABORATORY
                WHERE LAB_NAME = %s
            """, [lab_name])

            if cursor.fetchone():
                if is_ajax:
                    return JsonResponse({"error": "Lab already exists"}, status=400)
                return render(request, "add_lab.html", {
                    "error": "Lab already exists"
                })

            cursor.execute("""
                INSERT INTO LABORATORY (LAB_NAME)
                VALUES (%s)
            """, [lab_name])
        log_activity(lab_name, "Laboratory added", f"Lab:{lab_name}")

        if is_ajax:
            return JsonResponse({"success": True})
        return redirect("labs_list")

    return render(request, "add_lab.html")


# DELETE LAB
def delete_lab(request, id):

    id = validate_id(id)

    if not id:
        return render(request, "error.html", {
            "error": "Invalid ID"
        })

    with connection.cursor() as cursor:
        cursor.execute("SELECT LAB_NAME FROM LABORATORY WHERE LAB_ID = %s", [id])
        row = cursor.fetchone()
        lname = row[0] if row else f'ID:{id}'
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM LABORATORY WHERE LAB_ID = %s", [id])
    log_activity(lname, "Laboratory deleted", f"Lab ID:{id}")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True})
    return redirect("labs_list")


# GET LAB
def get_lab(request, id):

    id = validate_id(id)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if not id:
        if is_ajax:
            return JsonResponse({"error": "Invalid ID"}, status=400)
        return render(request, "error.html", {
            "error": "Invalid ID"
        })

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT *
            FROM LABORATORY
            WHERE LAB_ID = %s
        """, [id])

        lab = dictfetchall(cursor)
        lab = lab[0] if lab else None

    if is_ajax:
        return JsonResponse(lab or {}, safe=False)

    return render(request, "edit_lab.html", {
        "lab": lab
    })


# UPDATE LAB
def update_lab(request, id):

    id = validate_id(id)

    if not id:
        return render(request, "error.html", {
            "error": "Invalid ID"
        })

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == "POST":

        lab_name = request.POST.get("lab_name")

        if not lab_name:
            if is_ajax:
                return JsonResponse({"error": "Lab name required"}, status=400)
            return render(request, "edit_lab.html", {
                "error": "Lab name required"
            })

        with connection.cursor() as cursor:

            cursor.execute("""
                UPDATE LABORATORY
                SET LAB_NAME = %s
                WHERE LAB_ID = %s
            """, [lab_name, id])

        if is_ajax:
            return JsonResponse({"success": True})
        return redirect("labs_list")

    return redirect("labs_list")


# SEARCH LABS
def search_lab(request):

    name = request.GET.get("name")

    if not name:
        return redirect("labs_list")

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT *
            FROM LABORATORY
            WHERE LAB_NAME LIKE %s
            ORDER BY LAB_ID DESC
        """, ["%" + name + "%"])

        labs = dictfetchall(cursor)

    return render(request, "labs.html", {
        "labs": labs
    })

def labs_json(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM LABORATORY ORDER BY LAB_ID DESC")
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False)