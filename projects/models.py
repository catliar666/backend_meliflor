from django.db import models

# Create your models here.

class Alergia:
    def __init__(self, nombre, tipo, sintomas, tratamiento, gravedad, reaccion, fecha_diagnostico, observaciones):
        self.nombre = nombre
        self.tipo = tipo
        self.sintomas = sintomas
        self.tratamiento = tratamiento
        self.gravedad = gravedad
        self.reaccion = reaccion
        self.fecha_diagnostico = fecha_diagnostico
        self.observaciones = observaciones

