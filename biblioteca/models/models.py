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
    nacionalidad = fields.Char(string='Nacionalidad')
    cumpleautor = fields.Date(string='Fecha de nacimiento')
    biografia = fields.Text(string='Biografía')
    display_name = fields.Char(compute='_compute_display_name')
    book_ids = fields.One2many('biblioteca.libro', 'author_id', string='Libros escritos')

    @api.depends('firstname', 'lastname')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.firstname} {record.lastname}"

            
class BibliotecaEditorial(models.Model):
    _name = 'biblioteca.editorial'
    _description = 'biblioteca.editorial'
    _rec_name = 'firstname'
    
    firstname = fields.Char()
    display_name = fields.Char(compute='_compute_display_name')
    pais_ciudad = fields.Char(string='País o ciudad')
    fundacion = fields.Integer(string='Año de fundación')
    libro_ids = fields.One2many('biblioteca.libro', 'editorial', string='Libros publicados')

    @api.depends('firstname')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.firstname}"