from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import Database
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)


# Secret key is used by Flask to securely sign session data.
# In a real deployed application, this should be stored in an environment variable.
app.secret_key = os.getenv("SECRET_KEY")

database = Database()


# =========================
# HOME
# =========================

@app.route("/")
def home():

    posts = database.get_posts()

    return render_template(
        "index.html",
        posts=posts
    )


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return render_template(
                "register.html",
                error="Username and password are required."
            )

        # Check whether another account already uses this username.
        existing_user = database.get_user_by_username(username)

        if existing_user:
            return render_template(
                "register.html",
                error="Username already exists."
            )

        # Never store a user's plain-text password in the database.
        hashed_password = generate_password_hash(password)

        database.add_user(
            username,
            hashed_password
        )

        return redirect("/login")

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        user = database.get_user_by_username(username)

        # Verify the submitted password against the stored password hash.
        if not user or not check_password_hash(
            user[2],
            password
        ):
            return render_template(
                "login.html",
                error="Invalid username or password."
            )

        # Clear any previous session data before creating the new login session.
        session.clear()

        session["user_id"] = user[0]
        session["username"] = user[1]
        session["is_admin"] = bool(user[3])

        return redirect("/")

    return render_template("login.html")


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin():

    if not session.get("user_id"):
        return redirect("/login")

    # Only users marked as administrators can access this page.
    if not session.get("is_admin"):
        return "Unauthorized", 403

    posts = database.get_posts()
    users = database.get_users()

    return render_template(
        "admin.html",
        posts=posts,
        users=users
    )


# =========================
# ADMIN DELETE USER
# =========================

@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
def admin_delete_user(user_id):

    if not session.get("user_id"):
        return redirect("/login")

    if not session.get("is_admin"):
        return "Unauthorized", 403

    # Prevent an administrator from deleting their own account
    # through the admin user-management page.
    if user_id == session["user_id"]:
        return "You cannot delete your own admin account.", 400

    database.delete_user(user_id)

    return redirect("/admin")


# =========================
# PROFILE
# =========================

@app.route("/profile")
def profile():

    if not session.get("user_id"):
        return redirect("/login")

    user = database.get_user_by_username(
        session["username"]
    )

    posts = database.get_user_posts(
        session["user_id"]
    )

    return render_template(
        "profile.html",
        user=user,
        posts=posts
    )


# =========================
# DELETE ACCOUNT
# =========================

@app.route("/account/delete", methods=["POST"])
def delete_account():

    if not session.get("user_id"):
        return redirect("/login")

    database.delete_user(
        session["user_id"]
    )

    # Remove the login session after deleting the account.
    session.clear()

    return redirect("/")


# =========================
# CREATE POST
# =========================

@app.route("/post/create", methods=["GET", "POST"])
def create_post():

    if not session.get("user_id"):
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title or not content:
            return render_template(
                "create_post.html",
                error="Title and content are required."
            )

        database.add_post(
            title,
            content,
            session["user_id"]
        )

        return redirect("/")

    return render_template("create_post.html")


# =========================
# VIEW SINGLE POST
# =========================

@app.route("/post/<int:post_id>")
def view_post(post_id):

    post = database.get_post(post_id)

    if not post:
        return "Post not found", 404

    # Retrieve the post's comments and total number of likes
    # so they can be displayed on the post page.
    comments = database.get_comments(post_id)
    likes = database.count_likes(post_id)

    return render_template(
        "post.html",
        post=post,
        comments=comments,
        likes=likes
    )


# =========================
# EDIT POST
# =========================

@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):

    if not session.get("user_id"):
        return redirect("/login")

    post = database.get_post(post_id)

    if not post:
        return "Post not found", 404

    # Only the author of the post is allowed to edit it.
    if post[3] != session["user_id"]:
        return "Unauthorized", 403

    if request.method == "POST":

        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title or not content:
            return render_template(
                "edit_post.html",
                post=post,
                error="Title and content are required."
            )

        database.update_post(
            post_id,
            title,
            content
        )

        return redirect(f"/post/{post_id}")

    return render_template(
        "edit_post.html",
        post=post
    )


# =========================
# DELETE POST
# =========================

@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):

    if not session.get("user_id"):
        return redirect("/login")

    post = database.get_post(post_id)

    if not post:
        return "Post not found", 404

    is_owner = post[3] == session["user_id"]
    is_admin = session.get("is_admin", False)

    # A post can be deleted by either its owner or an administrator.
    if not is_owner and not is_admin:
        return "Unauthorized", 403

    database.delete_post(post_id)

    return redirect("/")


# =========================
# ADD COMMENT
# =========================

@app.route("/post/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):

    if not session.get("user_id"):
        return redirect("/login")

    post = database.get_post(post_id)

    if not post:
        return "Post not found", 404

    content = request.form["content"].strip()

    if content:
        database.add_comment(
            content,
            session["user_id"],
            post_id
        )

    return redirect(f"/post/{post_id}")


# =========================
# LIKE / UNLIKE POST
# =========================

@app.route("/post/<int:post_id>/like", methods=["POST"])
def like_post(post_id):

    if not session.get("user_id"):
        return redirect("/login")

    post = database.get_post(post_id)

    if not post:
        return "Post not found", 404

    user_id = session["user_id"]

    # Check whether this user has already liked the post.
    # If they have, remove the like; otherwise, add one.
    existing_like = database.check_like(
        user_id,
        post_id
    )

    if existing_like:
        database.remove_like(
            user_id,
            post_id
        )
    else:
        database.add_like(
            user_id,
            post_id
        )

    return redirect(f"/post/{post_id}")


# =========================
# SEARCH POSTS
# =========================

@app.route("/search")
def search():

    query = request.args.get("q", "").strip()

    if not query:
        return redirect("/")

    posts = database.search_posts(query)

    return render_template(
        "index.html",
        posts=posts,
        search_query=query
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    # Clear all session data so the user is logged out.
    session.clear()

    return redirect("/")


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)