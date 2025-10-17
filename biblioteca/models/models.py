from odoo import models, fields, api


class BibliotecaLibro(models.Model):
    _name = 'biblioteca.libro'
    _description = 'Libro de la Biblioteca'
    _rec_name = 'name'

    name = fields.Char(string='Título del Libro', required=True)
    author_id = fields.Many2one('biblioteca.autor', string='Autor')
    isbn = fields.Char(string='ISBN', required=True)
    editorial_id = fields.Many2one('biblioteca.editorial', string='Editorial')
    fechapubli = fields.Integer(string='Año de publicación')
    genero_id = fields.Many2one('biblioteca.genero', string='Género o Categoría')
    numpaginas = fields.Integer(string='Número de páginas', default=0)
    disponi = fields.Selection(
        [('disponible', 'Disponible'), ('prestado', 'Prestado'), ('reservado', 'Reservado')],
        string='Estado', default='disponible')
    ubicacion_id = fields.Many2one('biblioteca.ubicacion', string='Ubicación física')
    ejemplares = fields.Integer(string='Número de ejemplares', default=1)
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
            
            
class BibliotecaUsuario(models.Model):
    _name = 'biblioteca.usuario'
    _description = 'Usuario de Biblioteca'
    _rec_name = 'display_name'

    nombre = fields.Char(string='Nombre completo', required=True)
    dni = fields.Char(string='DNI o Identificación', required=True)
    cel = fields.Char(string='Teléfono')
    correo = fields.Char(string='Correo electrónico')
    direccion = fields.Char(string='Dirección')
    display_name = fields.Char(compute='_compute_display_name', store=True)
    prestamo_ids = fields.One2many(
        comodel_name='biblioteca.prestamo',
        inverse_name='usuario_id',
        string='Historial de préstamos'
    )

    @api.depends('nombre')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.nombre or 'Usuario sin nombre'


class BibliotecaPrestamo(models.Model):
    _name = 'biblioteca.prestamo'
    _description = 'Prestamo de libro'
    _rec_name = 'display_name'

    usuario_id = fields.Many2one('biblioteca.usuario', string='Usuario', required=True)
    libro_id = fields.Many2one('biblioteca.libro', string='Libro', required=True)
    fechaprestamo = fields.Date(string='Fecha de préstamo', required=True)
    fechadevolucion = fields.Date(string='Fecha de devolución')
    estado = fields.Selection([
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('atrasado', 'Atrasado'),
    ], string='Estado', default='activo', required=True)

    @api.depends('libro_id', 'usuario_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.libro_id.name or ''} - {record.usuario_id.nombre or ''}"
            
            
class BibliotecaPersonal(models.Model):
    _name = 'biblioteca.personal'
    _description = 'Personal de la Biblioteca'
    _rec_name = 'display_name'

    empleado = fields.Char(string='Nombre del empleado')
    cargo = fields.Selection([
        ('bibliotecario', 'Bibliotecario'),
        ('auxiliar', 'Auxiliar'),
        ('otro', 'Otro')
    ], string='Cargo')
    fechaingreso = fields.Date(string='Fecha de ingreso')
    contacto = fields.Char(string='Contacto')  

    @api.depends('empleado')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.empleado or ''


class BibliotecaMulta(models.Model):
    _name = 'biblioteca.multa'
    _description = 'Multa a Usuario'
    _rec_name = 'display_name'

    usuario_id = fields.Many2one(comodel_name='biblioteca.usuario', string='Usuario', required=True)
    monto = fields.Float(string='Monto', required=True)
    motivo = fields.Selection(
        [('retraso', 'Retraso'), ('dano', 'Daño'), ('perdida', 'Pérdida')],
        string='Motivo',
        required=True
    )
    fecha = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    estado = fields.Selection(
        [('pendiente', 'Pendiente'), ('pagado', 'Pagado')],
        string='Estado',
        required=True,
        default='pendiente'
    )
    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('usuario_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.usuario_id.nombre if record.usuario_id else 'Multa sin usuario'
