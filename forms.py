from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, PasswordField, StringField, TextAreaField, SubmitField, EmailField, TimeField
from wtforms.validators import DataRequired, Email, Length,NumberRange ,EqualTo

class ContattoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField('Telefono', validators=[Length(max=20)])
    messaggio = TextAreaField('Messaggio', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Invia Messaggio')


class PrenotazioneForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Telefono')  # opzionale, puoi aggiungere validatore se vuoi
    data = DateField('Data', validators=[DataRequired()], format='%Y-%m-%d')
    orario = TimeField('Orario', validators=[DataRequired()], format='%H:%M')
    persone = IntegerField('Numero persone', validators=[DataRequired(), NumberRange(min=1, max=20)])
    note = StringField('Note')  # opzionale
    submit = SubmitField('Prenota')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrati')
    
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Accedi')
    
    
#class Prenotazione(db.Model):
 #   id = db.Column(db.Integer, primary_key=True)
 #   nome = db.Column(db.String(50))
  #  email = db.Column(db.String(120))
 #   telefono = db.Column(db.String(20))
  #  data = db.Column(db.Date)
  #  orario = db.Column(db.Time)
  #  persone = db.Column(db.Integer)
   # note = db.Column(db.String(255))

#class Utente(db.Model):
 #   id = db.Column(db.Integer, primary_key=True)
  #  username = db.Column(db.String(50))
  #  email = db.Column(db.String(120))
  #  password_hash = db.Column(db.String(255))