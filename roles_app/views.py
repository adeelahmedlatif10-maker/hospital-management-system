from django.db import connection
from activity_logger import log_activity
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Helpers
def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def seed_default_roles():
    defaults = ['DOCTOR', 'TECH', 'OPERATOR', 'STAFF']
    with connection.cursor() as cursor:
        for role in defaults:
            cursor.execute("SELECT 1 FROM ROLES WHERE ROLE_NAME = %s", [role])
            if not cursor.fetchone():
                cursor.execute("INSERT INTO ROLES (ROLE_NAME) VALUES (%s)", [role])


def validate_id(id):
    try:
        id = int(id)
        return id if id > 0 else None
    except:
        return None

# ADD ROLE
def add_role(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if request.method == "POST":
        role_name = (request.POST.get("role_name") or "").strip().upper()
        if not role_name:
            if is_ajax:
                return JsonResponse({"error": "Role name required"}, status=400)
            return render(request, "add_roles.html", {"error": "Role name required"})
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO ROLES (ROLE_NAME) VALUES (%s)", [role_name])
            log_activity(role_name, "Role added", f"Role:{role_name}")
            if is_ajax:
                return JsonResponse({"success": True})
            return redirect("list_roles")
        except Exception as e:
            if is_ajax:
                return JsonResponse({"error": "Role already exists"}, status=400)
            return render(request, "add_roles.html", {"error": "Role already exists"})
    return render(request, "add_roles.html")


#   UPDATE ROLES
def update_role(request, id):
    id = validate_id(id)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if not id:
        if is_ajax:
            return JsonResponse({"error": "Invalid role id"}, status=400)
        return render(request, "error.html", {"error": "Invalid role id"})

    if request.method == "POST":
        role_name = (request.POST.get("role_name") or "").strip().upper()

        if not role_name:
            if is_ajax:
                return JsonResponse({"error": "Role name required"}, status=400)
            return render(request, "update_role.html", {"error": "Role name required"})

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE ROLES
                    SET ROLE_NAME = %s
                    WHERE ROLE_ID = %s
                """, [role_name, id])

            log_activity(role_name, "Role updated", f"Role ID:{id}")
            if is_ajax:
                return JsonResponse({"success": True})
            return redirect("list_roles")

        except Exception as e:
            if is_ajax:
                return JsonResponse({"error": str(e)}, status=400)
            return render(request, "update_role.html", {"error": str(e)})

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ROLE_ID, ROLE_NAME
            FROM ROLES
            WHERE ROLE_ID = %s
        """, [id])

        role = dictfetchall(cursor)

    if is_ajax:
        return JsonResponse(role[0] if role else {})
    return render(request, "update_role.html", {"role": role[0] if role else None})

# GET ROLE (JSON)
def get_role(request, id):
    id = validate_id(id)
    if not id:
        return JsonResponse({"error": "Invalid role id"}, status=400)
    with connection.cursor() as cursor:
        cursor.execute("SELECT ROLE_ID, ROLE_NAME FROM ROLES WHERE ROLE_ID = %s", [id])
        data = dictfetchall(cursor)
    return JsonResponse(data[0] if data else {}, safe=False)

#   DELETE ROLES
def delete_role(request, id):
   id = validate_id(id)
   is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

   if not id:
       if is_ajax:
           return JsonResponse({"error": "Invalid role id"}, status=400)
       return render(request,"error.html",{"error":"Invalid role id"})
   try:
       # First set ROLE_ID = NULL for all users having this role
       with connection.cursor() as cursor:
           cursor.execute("UPDATE USERS SET ROLE_ID = NULL WHERE ROLE_ID = %s", [id])
       with connection.cursor() as cursor:
           cursor.execute("""DELETE FROM ROLES WHERE ROLE_ID = %s""",[id])

       log_activity("Admin", "Role deleted", f"Role ID:{id}")
       if is_ajax:
           return JsonResponse({"success": True})
       return redirect("list_roles")
   
   except Exception as e:
       if is_ajax:
           return JsonResponse({"error": "Cannot delete role: " + str(e)}, status=400)
       return render(request,"roles.html",{"error": "Cannot delete role: " + str(e)})

def roles_json(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT ROLE_ID, ROLE_NAME FROM ROLES ORDER BY ROLE_NAME ASC")
        roles = dictfetchall(cursor)
    return JsonResponse(roles, safe=False)