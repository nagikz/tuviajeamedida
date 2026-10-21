from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, BooleanField
from wtforms.validators import Optional, NumberRange

class ExploradorDestinosForm(FlaskForm):
    class Meta:
        csrf = False
    
    entorno = SelectField(
        'Entorno deseado',
        choices=[('', 'Cualquier entorno'), ('playa', 'Playa'), ('montaña', 'Montaña'), ('ciudad', 'Ciudad')],
        validators=[Optional()]
    )
    sin_visado = BooleanField('Sin requisitos de visado previo', validators=[Optional()])


class ComparadorAlojamientosForm(FlaskForm):
    class Meta:
        csrf = False
        
    presupuesto_max = IntegerField(
        'Presupuesto máximo por noche (€)',
        validators=[Optional(), NumberRange(min=0, message="El precio no puede ser negativo")]
    )
    tipo = SelectField(
        'Modalidad de alojamiento',
        choices=[('', 'Cualquier modalidad'), ('hotel', 'Hotel'), ('hostal', 'Hostal'), ('cabaña', 'Cabaña'), ('apartamento', 'Apartamento')],
        validators=[Optional()]
    )
    desayuno = BooleanField('Imprescindible incluir desayuno', validators=[Optional()])
    mascotas = BooleanField('Permite viajar con mascotas', validators=[Optional()])


class AsistenteViajeMedidaForm(FlaskForm):
    class Meta:
        csrf = False
        
    entorno = SelectField(
        'Entorno de vacaciones',
        choices=[('', 'Cualquier entorno'), ('playa', 'Playa'), ('montaña', 'Montaña'), ('ciudad', 'Ciudad')],
        validators=[Optional()]
    )
    sin_visado = BooleanField('Viajar sin visado', validators=[Optional()])
    tipo = SelectField(
        'Tipo de alojamiento',
        choices=[('', 'Cualquier tipo'), ('hotel', 'Hotel'), ('hostal', 'Hostal'), ('cabaña', 'Cabaña'), ('apartamento', 'Apartamento')],
        validators=[Optional()]
    )
    presupuesto_max = IntegerField(
        'Gasto máximo por noche (€)',
        validators=[Optional(), NumberRange(min=0, message="El precio no puede ser negativo")]
    )
    desayuno = BooleanField('Requiere desayuno incluido', validators=[Optional()])
