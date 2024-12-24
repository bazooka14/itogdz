from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.load_tasks()

    def add_task(self, title, priority):
        task = {
            'id': self.next_id,
            'title': title,
            'priority': priority,
            'isDone': False
        }
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task

    def get_tasks(self):
        return self.tasks

    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['isDone'] = True
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                self.tasks.remove(task)
                self.save_tasks()
                return True
        return False

    def save_tasks(self):
        with open('tasks.txt', 'w') as f:
            json.dump(self.tasks, f, indent=4)

    def load_tasks(self):
        if os.path.exists('tasks.txt'):
            with open('tasks.txt', 'r') as f:
                self.tasks = json.load(f)
                if self.tasks:
                    self.next_id = max(task['id'] for task in self.tasks) + 1

task_manager = TaskManager()

@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    data = request.get_json()
    title = data.get('title')
    priority = data.get('priority')
    if not title or not priority:
        return jsonify({"error": "Missing 'title' or 'priority'"}), 400
    if priority not in ['low', 'normal', 'high']:
        return jsonify({"error": "Invalid 'priority' value"}), 400
    task = task_manager.add_task(title, priority)
    return jsonify(task), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_manager.get_tasks()), 200

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    if task_manager.complete_task(task_id):
        return '', 200
    return jsonify({"error": "Task not found"}), 404

@app.route('/tasks/delete', methods=['POST'])
def delete_task():
    if not request.is_json:
        return jsonify({"error": "Request body must be JSON"}), 400
    data = request.get_json()
    task_id = data.get('id')
    if not task_id:
        return jsonify({"error": "Task ID is required"}), 400
    if task_manager.delete_task(task_id):
        return '', 200
    return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
