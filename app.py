import datetime
import os.path

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, FlaskForm
from sqlalchemy import Column, String, Integer, select, Date, ForeignKey
from sqlalchemy.orm import relationship
from wtforms import IntegerField, SubmitField, DateField, SelectField, StringField
from wtforms.validators import DataRequired

db_exists = os.path.exists('db.sqlite')
app = Flask(__name__)
app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bootstrap = Bootstrap5(app)


class ExerciseType(db.Model):
    __tablename__ = 'exercise_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class Set(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    type_id = Column(Integer, ForeignKey('exercise_type.id'))
    reps = Column(Integer, nullable=False)
    weight = Column(Integer)
    type = relationship("ExerciseType")


if not db_exists:
    db.create_all()


class ExerciseTypeForm(FlaskForm):
    name = StringField('Name')
    submit = SubmitField()


class SetForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    type = SelectField('Type', coerce=int)
    reps = IntegerField('Reps', validators=[DataRequired()])
    weight = IntegerField('Weight')
    submit = SubmitField()


@app.route('/delete', methods=('POST',))
def delete():
    set_ = db.session.get(Set, request.args.get('id'))
    db.session.delete(set_)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/exercise_types', methods=('GET', 'POST'))
def exercise_types():
    if request.method == 'POST':
        db.session.add(ExerciseType(name=request.form['name']))
        db.session.commit()

    types = list(db.session.scalars(select(ExerciseType)))

    return render_template('exercise_types.html', types=types, type_form=ExerciseTypeForm(), ExerciseType=ExerciseType)


@app.route('/exercise_types/delete', methods=('POST',))
def delete_exercise_type():
    type_ = db.session.get(ExerciseType, request.args.get('id'))
    db.session.delete(type_)
    db.session.commit()
    return redirect('/exercise_types')


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        set_ = Set(
            date=datetime.date.fromisoformat(request.form['date']),
            type_id=int(request.form['type']),
            reps=int(request.form['reps']),
            weight=int(request.form['weight']) if request.form['weight'] else None
        )
        db.session.add(set_)
        db.session.commit()

    setform = SetForm()
    setform.type.choices = [(x.id, x.name) for x in db.session.scalars(select(ExerciseType))]
    sets = list(db.session.execute(select(Set.id, Set.date, ExerciseType.name, Set.reps).join(ExerciseType)))

    return render_template('index.html', sets=sets, setform=setform, Set=Set)


if __name__ == '__main__':
    app.run()
