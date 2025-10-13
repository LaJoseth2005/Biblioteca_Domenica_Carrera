from odoo import models, fields, api

class BibliotecaLibro(models.Model):
    _name = 'biblioteca.libro'
    _description = 'biblioteca.libro'
    _rec_name = 'firstname'
    
    firstname = fields.Char(string='Nombre Libro')
    author = fields.Many2one('biblioteca.autor', string='Autor Libro')
    isbn = fields.Char(string='ISBN')
    editorial = fields.Many2one('biblioteca.editorial', string='Editorial')
    fechapubli = fields.Integer(string='Año de publicación')
    genero = fields.Many2one('biblioteca.genero', string='Género o Categoría')
    numpaginas = fields.Integer(string='Número de páginas')
    disponi = fields.Selection([('disponible', 'Disponible'),('prestado', 'Prestado'),('reservado', 'Reservado')], string='Estado', default='disponible')
    ubi = fields.Many2one('biblioteca.ubicacion', string='Ubicación física')
    value = fields.Integer(string='Numero ejemplares')
    value2 = fields.Float(compute="_value_pc", store=True, string='Costo')
    description = fields.Text(string='Resumen Libro')

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

class BibliotecaAutor(models.Model):
    _name = 'biblioteca.autor'
    _description = 'biblioteca.autor'
    _rec_name = 'firstname'
    
    firstname = fields.Char()
    lastname = fields.Char()
    display_name = fields.Char(compute='_compute_display_name')

    @api.depends('firstname', 'lastname')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.firstname} {record.lastname}"