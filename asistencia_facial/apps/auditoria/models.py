"""
Este modelo registra las acciones realizadas por los usuarios, 
la accion, descripcion, fecha y la IP para saber desde donde se hizo
"""

from django.db import models
from apps.usuarios.models import Usuario


#Así es como se inserta SQL con el ORM de Django, se define una clase que hereda
#de models.Model y se definen los campos como atributos de la clase.

class Auditoria(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias'
    )
    accion = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=45, blank=True, null=True)

    #Meta es una clase interna que se utiliza para configurar el comportamiento del modelo
    class Meta:
        db_table = 'auditoria'
        verbose_name = 'Auditoria'
        verbose_name_plural = 'Auditorias'
        ordering = ['-fecha']

    #Define como se representa el objeto como texto
    def __str__(self):
        return f'{self.usuario} - {self.accion} - {self.fecha}'