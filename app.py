import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT f.id, f.nombre, f.fecha_creacion,
        GROUP_CONCAT(p.imagen, ',') as imagenes
        FROM formaciones f
        LEFT JOIN formacion_personajes fp ON f.id = fp.formacion_id
        LEFT JOIN personajes p ON fp.personaje_id = p.id
        GROUP BY f.id
        ORDER BY f.fecha_creacion ASC
    """).fetchall()
    formaciones = []
    for i, row in enumerate(rows, 1):
        formacion = dict(row)
        formacion["num"] = i
        formaciones.append(formacion)
    conn.close()
    return render_template("index.html", formaciones=formaciones)

@app.route("/crear", methods=["GET", "POST"])
def crear():
    conn = get_db_connection()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip() or None
        personajes_ids = request.form.getlist("personajes")

        if len(personajes_ids) != 4:
            conn.close()
            personajes = conn.execute("SELECT * FROM personajes ORDER BY id").fetchall()
            return render_template("crear.html", personajes=personajes, error="Debes seleccionar exactamente 4 personajes")

        cursor = conn.execute(
            "INSERT INTO formaciones (nombre) VALUES (?)",
            (nombre,)
        )
        formacion_id = cursor.lastrowid

        for orden, pid in enumerate(personajes_ids, 1):
            conn.execute(
                "INSERT INTO formacion_personajes (formacion_id, personaje_id, orden) VALUES (?, ?, ?)",
                (formacion_id, pid, orden)
            )

        conn.commit()
        conn.close()
        return redirect(url_for("ver", id=formacion_id))

    personajes = conn.execute("SELECT * FROM personajes ORDER BY id").fetchall()
    conn.close()
    return render_template("crear.html", personajes=personajes)

@app.route("/formacion/<int:id>")
def ver(id):
    conn = get_db_connection()
    formacion = conn.execute("SELECT * FROM formaciones WHERE id = ?", (id,)).fetchone()
    personajes = conn.execute("""
        SELECT p.*, fp.orden
        FROM formacion_personajes fp
        JOIN personajes p ON fp.personaje_id = p.id
        WHERE fp.formacion_id = ?
        ORDER BY fp.orden
    """, (id,)).fetchall()
    all_ids = [r[0] for r in conn.execute(
        "SELECT id FROM formaciones ORDER BY fecha_creacion ASC"
    ).fetchall()]
    num = all_ids.index(id) + 1 if id in all_ids else len(all_ids)
    conn.close()
    if formacion is None:
        return redirect(url_for("index"))
    return render_template("ver.html", formacion=formacion, personajes=personajes, num=num)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_db_connection()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip() or None
        personajes_ids = request.form.getlist("personajes")

        if len(personajes_ids) != 4:
            formacion = conn.execute("SELECT * FROM formaciones WHERE id = ?", (id,)).fetchone()
            personajes = conn.execute("SELECT * FROM personajes ORDER BY id").fetchall()
            actuales = conn.execute(
                "SELECT personaje_id FROM formacion_personajes WHERE formacion_id = ?", (id,)
            ).fetchall()
            actuales_ids = [str(row["personaje_id"]) for row in actuales]
            conn.close()
            return render_template("editar.html", formacion=formacion, personajes=personajes, actuales_ids=actuales_ids, error="Debes seleccionar exactamente 4 personajes")

        conn.execute("UPDATE formaciones SET nombre = ? WHERE id = ?", (nombre, id))
        conn.execute("DELETE FROM formacion_personajes WHERE formacion_id = ?", (id,))

        for orden, pid in enumerate(personajes_ids, 1):
            conn.execute(
                "INSERT INTO formacion_personajes (formacion_id, personaje_id, orden) VALUES (?, ?, ?)",
                (id, pid, orden)
            )

        conn.commit()
        conn.close()
        return redirect(url_for("ver", id=id))

    formacion = conn.execute("SELECT * FROM formaciones WHERE id = ?", (id,)).fetchone()
    personajes = conn.execute("SELECT * FROM personajes ORDER BY id").fetchall()
    actuales = conn.execute(
        "SELECT personaje_id FROM formacion_personajes WHERE formacion_id = ?", (id,)
    ).fetchall()
    actuales_ids = [str(row["personaje_id"]) for row in actuales]
    conn.close()
    return render_template("editar.html", formacion=formacion, personajes=personajes, actuales_ids=actuales_ids)

@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM formacion_personajes WHERE formacion_id = ?", (id,))
    conn.execute("DELETE FROM formaciones WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
