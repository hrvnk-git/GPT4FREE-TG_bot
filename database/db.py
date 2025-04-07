import aiosqlite

DB_FILE = "history.db"


async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_history (
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_modes (
                user_id INTEGER PRIMARY KEY,
                mode TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS response_ids (
                user_id INTEGER PRIMARY KEY,
                response_id TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS authorized_users (
                user_id INTEGER PRIMARY KEY,
                admin INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def save_message(user_id: int, role: str, content: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO message_history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )
        await db.commit()


async def load_history(user_id: int, max_len: int):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT role, content FROM message_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, max_len),
        )
        rows = await cursor.fetchall()
        # Вернуть в хронологическом порядке (от старых к новым)
        return list(
            reversed([{"role": role, "content": content} for role, content in rows])
        )


async def load_user_mode(user_id: int) -> str:
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT mode FROM user_modes WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        else:
            # Значение по умолчанию - "Ответ текстом"
            return "Ответ текстом"


async def save_user_mode(user_id: int, mode: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "REPLACE INTO user_modes (user_id, mode) VALUES (?, ?)", (user_id, mode)
        )
        await db.commit()


async def load_response_id(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT response_id FROM response_ids WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        else:
            # Значение по умолчанию - None
            return None


async def save_response_id(user_id: int, response_id: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "REPLACE INTO response_ids (user_id, response_id) VALUES (?, ?)",
            (user_id, response_id),
        )
        await db.commit()


async def delete_response_id(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM response_ids WHERE user_id = ?", (user_id,))
        await db.commit()


async def delete_history(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM message_history WHERE user_id = ?", (user_id,))
        await db.commit()


async def add_authorized_user(user_id: int, admin: int = 0):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT OR REPLACE INTO authorized_users (user_id, admin) VALUES (?, ?)",
            (user_id, admin),
        )
        await db.commit()


async def load_authorized_user(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "SELECT user_id FROM authorized_users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]
        else:
            # Значение по умолчанию - None
            return None
