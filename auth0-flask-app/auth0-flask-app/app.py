
import os

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    g
)
from dotenv import load_dotenv
from auth0_server_python.auth_types import LogoutOptions
from auth import auth0

load_dotenv()

app = Flask(__name__)

# Secret key used to protect Flask sessions
app.secret_key = os.getenv("AUTH0_SECRET")

if not app.secret_key:
    raise RuntimeError(
        "AUTH0_SECRET is missing. Check your .env file."
    )

# Local development cookie settings
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)


@app.before_request
def store_request_options():
    g.store_options = {"request": request}


@app.route("/")
async def index():
    """Display the home page."""
    user = await auth0.get_user(g.store_options)
    return render_template("index.html", user=user)


@app.route("/login")
async def login():
    """Redirect the user to Auth0 login."""
    authorization_url = await auth0.start_interactive_login(
        {},
        g.store_options
    )
    return redirect(authorization_url)


@app.route("/callback")
async def callback():
    """Handle the response returned by Auth0."""

    # Show an understandable message if authorization is denied.
    error = request.args.get("error")

    if error:
        description = request.args.get(
            "error_description",
            "Authorization was not completed."
        )

        app.logger.warning(
            "Auth0 authorization error: %s - %s",
            error,
            description
        )

        return (
            f"Auth0 authorization failed: {error}. "
            f"{description}. Please return to the home page "
            "and try logging in again.",
            400
        )

    try:
        await auth0.complete_interactive_login(
            str(request.url),
            g.store_options
        )

        app.logger.info("Auth0 login completed successfully.")
        return redirect(url_for("index"))

    except Exception as e:
        app.logger.exception("Auth0 callback failed")

        return (
            "Login failed while processing the Auth0 callback. "
            f"Error type: {type(e).__name__}. "
            "Check the Flask terminal for details.",
            400
        )


@app.route("/profile")
async def profile():
    """Display the profile of the logged-in user."""
    user = await auth0.get_user(g.store_options)

    if not user:
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


@app.route("/logout")
async def logout():
    """Log out the user through Auth0."""
    options = LogoutOptions(
        return_to=url_for("index", _external=True)
    )

    logout_url = await auth0.logout(
        options,
        g.store_options
    )

    return redirect(logout_url)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
