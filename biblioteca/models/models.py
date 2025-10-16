from odoo import models, fields, api

class BibliotecaLibro(models.Model):
    _name = 'biblioteca.libro'
    _description = 'Libro de la Biblioteca'
    _rec_name = 'name'  # Mejor usar un campo llamado 'name' para el título del libro

    name = fields.Char(string='Título del Libro', required=True)
    author_id = fields.Many2one('biblioteca.autor', string='Autor')
    isbn = fields.Char(string='ISBN')
    editorial_id = fields.Many2one('biblioteca.editorial', string='Editorial')
    fechapubli = fields.Integer(string='Año de publicación')
    genero_id = fields.Many2one('biblioteca.genero', string='Género o Categoría')
    numpaginas = fields.Integer(string='Número de páginas')
    disponi = fields.Selection(
        [('disponible', 'Disponible'), ('prestado', 'Prestado'), ('reservado', 'Reservado')],
        string='Estado', default='disponible')
    ubicacion_id = fields.Many2one('biblioteca.ubicacion', string='Ubicación física')
    ejemplares = fields.Integer(string='Número de ejemplares')
    costo = fields.Float(compute="_compute_costo", store=True, string='Costo')
    description = fields.Text(string='Resumen')

    @api.depends('ejemplares')
    def _compute_costo(self):
        for record in self:
            record.costo = (record.ejemplares or 0) / 100


class BibliotecaAutor(models.Model):
    _name = 'biblioteca.autor'
    _description = 'Autor de la Biblioteca'
    _rec_name = 'display_name'

    firstname = fields.Char(string='Nombre')
    lastname = fields.Char(string='Apellido')
    nacionalidad = fields.Char(string='Nacionalidad')
    cumpleautor = fields.Date(string='Fecha de nacimiento')
    biografia = fields.Text(string='Biografía')
    display_name = fields.Char(compute='_compute_display_name', store=True)
    book_ids = fields.One2many('biblioteca.libro', 'author_id', string='Libros escritos')

    @api.depends('firstname', 'lastname')
    def _compute_display_name(self):
        for record in self:
            parts = [record.firstname or '', record.lastname or '']
            record.display_name = ' '.join([p for p in parts if p]).strip()


class BibliotecaEditorial(models.Model):
    _name = 'biblioteca.editorial'
    _description = 'Editorial de la Biblioteca'
    _rec_name = 'display_name'

    editorial = fields.Char(string='Nombre')
    display_name = fields.Char(compute='_compute_display_name', store=True)
    ciudad = fields.Char(string='Ciudad o País')
    fundacion = fields.Integer(string='Año de fundación')
    libro_ids = fields.One2many('biblioteca.libro', 'editorial_id', string='Libros publicados')

    @api.depends('editorial')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.editorial or ''


class BibliotecaGenero(models.Model):
    _name = 'biblioteca.genero'
    _description = 'Género o Categoría'
    _rec_name = 'display_name'

    genero = fields.Char(string='Nombre del género', required=True)
    descripcion = fields.Text(string='Descripción breve')
    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('genero')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.genero or ''

class BibliotecaUbicacion(models.Model):
    _name = 'biblioteca.ubicacion'
    _description = 'Ubicación Física'
    _rec_name = 'display_name'

    ubicacion = fields.Char(string='Nombre del bloque o sala', required=True)
    descripcion = fields.Text(string='Descripción o referencia física')
    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('ubicacion')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.ubicacion or ''