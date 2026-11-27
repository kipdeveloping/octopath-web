import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            clase TEXT NOT NULL,
            imagen TEXT,
            hp INTEGER NOT NULL,
            ph INTEGER NOT NULL,
            nivel INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS formaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS formacion_personajes (
            formacion_id INTEGER NOT NULL,
            personaje_id INTEGER NOT NULL,
            orden INTEGER NOT NULL,
            PRIMARY KEY (formacion_id, personaje_id),
            FOREIGN KEY (formacion_id) REFERENCES formaciones(id) ON DELETE CASCADE,
            FOREIGN KEY (personaje_id) REFERENCES personajes(id)
        )
    """)

    personajes = [
        ("Ophilia", "Clerigo", "ophilia.png", 280, 350),
        ("Cyrus", "Erudito", "cyrus.png", 240, 380),
        ("Olberic", "Guerrero", "olberic.png", 420, 180),
        ("Alfyn", "Boticario", "alfyn.png", 300, 300),
        ("H'aanit", "Cazador", "haanit.png", 320, 280),
        ("Tressa", "Mercader", "tressa.png", 290, 260),
        ("Therion", "Ladron", "therion.png", 270, 240),
        ("Primrose", "Bailarin", "primrose.png", 260, 320),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO personajes (nombre, clase, imagen, hp, ph) VALUES (?, ?, ?, ?, ?)",
        personajes
    )

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    init_db()
