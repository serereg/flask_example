from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:password@localhost/project_tracker"
app.config["SECRET_KEY"] = b'on\xbe\x95aC|\xfc\xf2\xaa\xa3\xff\x85\xf1\xb7\xfd\xe9@\xee\x04\xaa\xd6\x03\xd9'
db = SQLAlchemy(app)


class Project(db.Model):
    __tablename__ = 'projects'
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=50))

    task = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(db.Model):
    __tablename__ = "tasks"
    
    task_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    description = db.Column(db.String(length=50))

    project = db.relationship("Project", back_populates="task")


@app.route("/")
def show_projects():
    return render_template("index.html", projects=Project.query.all())


@app.route("/projects/<project_id>")
def show_tasks(project_id):
    return render_template("project-tasks.html", project=Project.query.filter_by(project_id=project_id).first(),
                           tasks=Task.query.filter_by(project_id=project_id).all()
                           )


@app.route("/add/project", methods=["POST"])
def add_project():
    if not request.form['project-title']:
        flash('Enter a title for the project', 'red')
    else:
        project = Project(title=request.form['project-title'])
        db.session.add(project)
        db.session.commit()
        flash("Project added successfully", "green")
    return redirect(url_for('show_projects'))


@app.route("/add/task/<project_id>", methods=["POST"])
def add_task(project_id):
    if not request.form['task-name']:
        flash('Enter a name for the task', 'red')
    else:
        task = Task(description=request.form['task-name'], project_id=project_id)
        db.session.add(task)
        db.session.commit()
        flash("Task added successfully", "green")
    return redirect(url_for('show_tasks', project_id=project_id))


@app.route("/delete/task/<task_id>", methods=["POST"])
def delete_task(task_id):
    pending_delete_task = Task.query.filter_by(task_id=task_id).first()
    original_project_id = pending_delete_task.project.project_id
    db.session.delete(pending_delete_task)
    db.session.commit()
    return redirect(url_for('show_tasks', project_id=original_project_id))


@app.route("/delete/project/<project_id>", methods=["POST"])
def delete_project(project_id):
    pending_delete_project = Project.query.filter_by(project_id=project_id).first()
    db.session.delete(pending_delete_project)
    db.session.commit()
    return redirect(url_for("show_projects"))


app.run(debug=True, host="0.0.0.0", port=8000)
