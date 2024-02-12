from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from sqlite3 import Error

# Initialize FastAPI app
app = FastAPI()

# SQLite database file path
DATABASE_PATH = "todo.db"

# Define Pydantic model for Task
class Task(BaseModel):
    title: str
    description: str

# Function to create a connection to the SQLite database
def create_connection():
    try:
        connection = sqlite3.connect(DATABASE_PATH)
        print("Connection to SQLite DB successful")
        return connection
    except Error as e:
        print(f"The error '{e}' occurred")

# Create table if it doesn't exist
def create_table():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        );
    """)
    connection.commit()

# Routes
@app.post("/tasks/")
async def create_task(task: Task):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (task.title, task.description))
    connection.commit()
    task_id = cursor.lastrowid
    connection.close()
    return {"id": task_id, **task.dict()}

@app.get("/tasks/")
async def read_tasks():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    connection.close()
    return [{"id": task[0], "title": task[1], "description": task[2]} for task in tasks]

@app.get("/tasks/{task_id}")
async def read_task(task_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    connection.close()
    if task:
        return {"id": task[0], "title": task[1], "description": task[2]}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: Task):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE tasks SET title = ?, description = ? WHERE id = ?", (task.title, task.description, task_id))
    connection.commit()
    connection.close()
    return {"id": task_id, **task.dict()}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    connection.close()
    return {"message": "Task deleted successfully"}

# Create table if it doesn't exist
create_table()

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
