import datetime
import os.path

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, FlaskForm
from sqlalchemy import Column, String, Integer, select, Date
from wtforms import StringField, IntegerField, SubmitField, DateField
from wtforms.validators import DataRequired

db_exists = os.path.exists('db.sqlite')
app = Flask(__name__)
app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
bootstrap = Bootstrap5(app)


class Set(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    exercise = Column(String, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Integer)


if not db_exists:
    db.create_all()


class SetForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    exercise = StringField('Exercise', validators=[DataRequired()])
    reps = IntegerField('Reps', validators=[DataRequired()])
    weight = IntegerField('Weight')
    submit = SubmitField()


@app.route('/delete', methods=('POST',))
def delete():
    set_ = db.session.get(Set, request.args.get('id'))
    db.session.delete(set_)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        set_ = Set(
            date=datetime.date.fromisoformat(request.form['date']),
            exercise=request.form['exercise'],
            reps=int(request.form['reps']),
            weight=int(request.form['weight']) if request.form['weight'] else None
        )
        db.session.add(set_)
        db.session.commit()

    stmt = select(Set)
    sets = list(db.session.scalars(stmt))

    return render_template('index.html', sets=sets, setform=SetForm(), Set=Set)


if __name__ == '__main__':
    app.run()
