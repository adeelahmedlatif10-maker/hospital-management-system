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

#   ADD USERS
def add_user(request):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role_id = request.POST.get('role_id')

        if not username or not password:
            if is_ajax:
                return JsonResponse({"error": "All fields are required"}, status=400)
            return render(request,"add_user.html",{"error": "All fields are required"})
        
        if len(username) < 3:
            if is_ajax:
                return JsonResponse({"error": "Username is too short"}, status=400)
            return render (request,"add_user.html",{"error" : "Username is too short"})
        
        if len(password) < 4:
            if is_ajax:
                return JsonResponse({"error": "Password is too short"}, status=400)
            return render (request,"add_user.html",{"error" : "Password is too short"})
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM USERS WHERE USER_NAME = %s", [username])
            if cursor.fetchone():
                if is_ajax:
                    return JsonResponse({"error": "Username already exists"}, status=400)
                return render(request, "add_user.html", {"error": "Username already exists"})
            
        if role_id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM ROLES WHERE ROLE_ID = %s",[role_id])
                if not cursor.fetchone():
                    if is_ajax:
                        return JsonResponse({"error":"Invalid role_id"}, status=400)
                    return render(request,"add_user.html",{"error":"Invalid role_id"})
                
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO USERS (USER_NAME,USER_PASSWORD,ROLE_ID)
                           VALUES (%s,%s,%s)
                           """,[username,password,role_id if role_id else None])
        log_activity(username, "User created", f"Role:{role_id}")
        if is_ajax:
            return JsonResponse({"success": True})
        return redirect("list_users")
    
    return render (request,"add_user.html")

#   DELETE USERS
def delete_user(request,id):
    id = validate_id(id)
    if not id:
        return render(request,"error.html",{"error":"Inalid role id"})
    
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM USERS WHERE USER_ID = %s",[id])
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"success": True})
    return redirect("users_list")

#   GET USER
def get_user(request, id):
    id = validate_id(id)
    if not id:
        return render(request, "error.html", {"error": "Invalid ID"})

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT USER_ID, USER_NAME, ROLE_ID
            FROM USERS
            WHERE USER_ID = %s
        """, [id])

        user = dictfetchall(cursor)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(user[0] if user else {}, safe=False)

    return render(request, "edit_user.html", {"user": user[0] if user else None})


def update_user(request,id):
    id = validate_id(id)

    if not id:
        return render(request,"error.html",{"error":"Invalid id"})
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get ('password')
        role_id = request.POST.get('role_id')

        if not username:
            return render(request,"edit_user.html",{"error":"Invalid Username"})
        
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT * FROM USERS
                           WHERE USER_NAME = %s AND USER_ID !=%s
                           """,[username,id])
            if cursor.fetchone():
                return render(request,"edit_user.html",{"error":"Username already exists"})
            
        if role_id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM ROLES WHERE ROLE_ID = %s", [role_id])
                if not cursor.fetchone():
                    return render(request, "edit_user.html", {"error": "Invalid role"})
        
        with connection.cursor() as cursor:
            if password:
                cursor.execute("""UPDATE USERS
                    SET USER_NAME=%s, USER_PASSWORD=%s, ROLE_ID=%s
                    WHERE USER_ID=%s""",[username,password,role_id,id])
            else:
                cursor.execute("""
                               UPDATE USERS 
                               SET USER_NAME=%s, ROLE_ID =%s
                               WHERE USER_ID = %s
                               """,[username,role_id,id])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": True})

        return redirect("users_list")
    
    return redirect("users_list")

def users_json(request):
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT U.USER_ID, U.USER_NAME, R.ROLE_NAME as role, U.CREATED_AT
                       FROM USERS U
                       LEFT JOIN ROLES R ON U.ROLE_ID = R.ROLE_ID
                       ORDER BY U.CREATED_AT DESC
                       """)
        data = dictfetchall(cursor)
    return JsonResponse(data, safe=False)


def login_view(request):
    """
    POST: {username, password}  →  {success, user_id, username, role_id, role_name}
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    username = (request.POST.get("username") or "").strip()
    password = (request.POST.get("password") or "").strip()

    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT U.USER_ID, U.USER_NAME, U.USER_PASSWORD,
                   COALESCE(R.ROLE_ID, 0)   AS ROLE_ID,
                   COALESCE(R.ROLE_NAME, '') AS ROLE_NAME
            FROM USERS U
            LEFT JOIN ROLES R ON U.ROLE_ID = R.ROLE_ID
            WHERE LOWER(U.USER_NAME) = LOWER(%s)
        """, [username])
        user = cursor.fetchone()

    if not user:
        return JsonResponse({"error": "Invalid username or password"}, status=401)

    uid, uname, stored_pass, role_id, role_name = user

    if stored_pass != password:
        return JsonResponse({"error": "Invalid username or password"}, status=401)

    log_activity(uname, "User logged in", f"Role: {role_name}")

    return JsonResponse({
        "success":   True,
        "user_id":   uid,
        "username":  uname,
        "role_id":   role_id,
        "role_name": role_name,
    })


def logout_view(request):
    log_activity(
        request.POST.get("username") or "unknown",
        "User logged out", ""
    )
    return JsonResponse({"success": True})
