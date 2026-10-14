"""Task API - prosta aplikacja webowa do zarządzania zadaniami (Flask + PostgreSQL)."""
import os
import socket

from flask import Flask, jsonify, request
from sqlalchemy import Boolean, Column, Integer, MetaData, String, Table, create_engine, insert, select, text, update

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "local")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")

metadata = MetaData()
tasks = Table(
    "tasks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("title", String(200), nullable=False),
    Column("done", Boolean, nullable=False, default=False),
)


def create_app(database_url=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.compact = False
    engine = create_engine(database_url or DATABASE_URL, pool_pre_ping=True)
    metadata.create_all(engine)
    engine.dispose()  # połączenia otwierane osobno w każdym procesie gunicorna

    @app.get("/")
    def index():
        return jsonify(
            app="Task API",
            message="Witaj w aplikacji Task API!",
            version=APP_VERSION,
            environment=APP_ENV,
            host=socket.gethostname(),
        )

    @app.get("/health")
    def health():
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify(status="ok", database="ok", version=APP_VERSION)

    @app.get("/tasks")
    def list_tasks():
        with engine.connect() as conn:
            rows = conn.execute(select(tasks).order_by(tasks.c.id)).mappings().all()
        return jsonify([dict(r) for r in rows])

    @app.post("/tasks")
    def create_task():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify(error="Pole 'title' jest wymagane"), 400
        with engine.begin() as conn:
            new_id = conn.execute(insert(tasks).values(title=title, done=False)).inserted_primary_key[0]
        return jsonify(id=new_id, title=title, done=False), 201

    @app.patch("/tasks/<int:task_id>")
    def mark_done(task_id):
        data = request.get_json(silent=True) or {}
        done = bool(data.get("done", True))
        with engine.begin() as conn:
            result = conn.execute(update(tasks).where(tasks.c.id == task_id).values(done=done))
            if result.rowcount == 0:
                return jsonify(error="Nie znaleziono zadania"), 404
            row = conn.execute(select(tasks).where(tasks.c.id == task_id)).mappings().one()
        return jsonify(dict(row))

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8000)
