"""Legacy backend entrypoint.

Keep this file as a thin wrapper so older launch commands like
`uvicorn main:app --reload` continue to work while the app itself lives in
`app.main`.
"""

from app.main import app
