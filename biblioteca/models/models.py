from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import requests

class BibliotecaLibro(models.Model):
    _name = 'biblioteca.libro'
    _description = 'Libro de la Biblioteca'
    _rec_name = 'name'

    name = fields.Char(string='Título del Libro', required=False)
    author_id = fields.Many2one('biblioteca.autor', string='Autor')
    isbn = fields.Char(string='ISBN', required=False)
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
            
    def action_importar_libro(self):
        for record in self:
            if not record.isbn:
                raise ValidationError("Debes ingresar un ISBN antes de importar.")
            record.importar_libro_por_isbn(record.isbn)

    @api.model
    def importar_libro_por_isbn(self, isbn):
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        response = requests.get(url)
        data = response.json()

        libro_data = data.get(f"ISBN:{isbn}")
        if not libro_data:
            raise ValidationError("No se encontró información para este ISBN en OpenLibrary.")

        titulo = libro_data.get('title', 'Sin título')

        autores = libro_data.get('authors', [])
        autor_nombre = autores[0]['name'] if autores else 'Autor desconocido'
        autor_split = autor_nombre.split()
        firstname = autor_split[0] if autor_split else 'Nombre'
        lastname = ' '.join(autor_split[1:]) if len(autor_split) > 1 else 'Apellido'
        autor = self.env['biblioteca.autor'].search([
            ('firstname', '=', firstname),
            ('lastname', '=', lastname)
        ], limit=1)
        if not autor:
            autor = self.env['biblioteca.autor'].create({
                'firstname': firstname,
                'lastname': lastname,
                'nacionalidad': 'Desconocida'
            })

        generos = libro_data.get('subjects', [])
        genero_nombre = generos[0]['name'] if generos else 'General'
        genero = self.env['biblioteca.genero'].search([('genero', '=', genero_nombre)], limit=1)
        if not genero:
            genero = self.env['biblioteca.genero'].create({
                'genero': genero_nombre,
                'descripcion': 'Importado desde OpenLibrary'
            })

        fecha_publi = libro_data.get('publish_date', '')
        try:
            fechapubli = int(fecha_publi[-4:]) if fecha_publi else 0
        except:
            fechapubli = 0

        paginas = libro_data.get('number_of_pages', 0)

        resumen = libro_data.get('notes', '')

        nuevo_libro = self.write({
            'name': titulo,
            'isbn': isbn,
            'author_id': autor.id,
            'genero_id': genero.id,
            'fechapubli': fechapubli,
            'numpaginas': paginas,
            'description': resumen,
        })

        return nuevo_libro

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

    nombre = fields.Char(string='Nombre completo', required=True )
    dni = fields.Char(string='DNI o Identificación', required=True, size=10)
    cel = fields.Char(string='Teléfono')
    correo = fields.Char(string='Correo electrónico')
    direccion = fields.Char(string='Dirección')
    display_name = fields.Char(compute='_compute_display_name', store=True)
    tipousuario= fields.Selection(selection=[('alumno', 'Alumno'),
                                              ('profesor', 'Profesor'),
                                              ('personal', 'Personal'),
                                              ('externo', 'Usuario externo')],string='Tipo de usuario')
    historialprestamo= fields.Char(string='Historial de prestamo')
    prestamo_ids = fields.One2many(
        comodel_name='biblioteca.prestamo',
        inverse_name='usuario_id',
        string='Historial de préstamos'
    )

    @api.depends('nombre')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.nombre or 'Usuario sin nombre'

    @api.constrains('dni')
    def _check_dni(self):
        for record in self:
            if record.dni:
                es_valido, mensaje = self.validar_cedula(record.dni)
                if not es_valido:
                    raise ValidationError(mensaje)

    def validar_cedula(self, cedula):
        if len(cedula) != 10:
            return (False, "La cédula debe tener exactamente 10 dígitos")
        if not cedula.isdigit():
            return (False, "La cédula solo debe contener números")
        provincia = int(cedula[:2])
        if provincia < 1 or provincia > 24:
            return (False, "Los primeros dos dígitos deben corresponder a una provincia ecuatoriana (01–24)")
        tercer_digito = int(cedula[2])
        if tercer_digito < 0 or tercer_digito > 6:
            return (False, "El tercer dígito debe estar entre 0 y 6")
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        digito_verificador = int(cedula[-1])
        suma = 0
        for i in range(9):
            valor = int(cedula[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor
        digito_calculado = (10 - (suma % 10)) % 10
        if digito_calculado != digito_verificador:
            return (False, f"Dígito verificador incorrecto.")
        return (True, "Cédula válida")

class BibliotecaWizard(models.TransientModel):
    _name = "biblioteca.wizard"
    _description = "Wizard para devolucion de prestamo"
    
    prestamo_id= fields.Many2one('biblioteca.prestamo')
    motivo_multa = fields.Selection([
        ('re', 'Retraso'),
        ('da', 'Daño'),
        ('pe', 'Pérdida'),
    ], string='Motivo de multa', default='b')
    observaciones=fields.Char(string='Observaciones')
    
    def cerrar_prestamo(self):
        self.prestamo_id.motivo_multa = self.motivo_multa
        self.prestamo_id.observaciones = self.observaciones
        self.prestamo_id.estado = 'd'
        print("caca")
        
class BibliotecaPrestamo(models.Model):
    _name = 'biblioteca.prestamo'
    _description = 'Prestamo de libro'
    _rec_name = 'name'

    name = fields.Char(string="Código Prestamo")
    usuario_id = fields.Many2one('biblioteca.usuario', string='Usuario', required=True)
    libro_id = fields.Many2many('biblioteca.libro', string='Libro', required=True)
    fechaprestamo = fields.Datetime(default=datetime.now(), string='Fecha de préstamo')
    fechadevolucion = fields.Date(string='Fecha de devolución')
    estado = fields.Selection([
        ('b', 'Borrador'),
        ('p', 'Préstamo'),
        ('m', 'Multa'),
        ('d', 'Devuelto'),
    ], string='Estado', default='b')
    observaciones=fields.Char(string='Observaciones')
    multabool = fields.Boolean(default=False)
    multa = fields.Float(string='Monto de multa')
    multa_id = fields.One2many('biblioteca.multa', 'prestamo', string='Multa')
    motivo_multa = fields.Selection([
        ('re', 'Retraso'),
        ('da', 'Daño'),
        ('pe', 'Pérdida'),
    ], string='Motivo de multa')

    fechamax = fields.Datetime(compute='_compute_fecha_devo', string='Fecha máxima de devolución', store=True)
    personalprestamo = fields.Many2one('biblioteca.personal', string='Personal de préstamo')

    def action_aplicar_multa(self):
        """Cambia estado a multa y crea registro en biblioteca.multa."""
        for prestamo in self:
            if prestamo.estado == 'm':
                continue

            monto = 0.0
            if prestamo.motivo_multa == 're':
                monto = 2.0
            elif prestamo.motivo_multa == 'da':
                monto = 4.0
            elif prestamo.motivo_multa == 'pe':
                monto = 6.0

            prestamo.write({
                'estado': 'm',
                'multabool': True,
                'multa': monto,
            })

            self.env['biblioteca.multa'].create({
                'usuario_id': prestamo.usuario_id.id,
                'monto': monto,
                'motivo': prestamo.motivo_multa or 're',
                'fecha': datetime.now().date(),
                'estado': 'pen',
                'prestamo': prestamo.id,
            })


    @api.depends('fechaprestamo')
    def _compute_fecha_devo(self):
        for record in self:
            record.fechamax = record.fechaprestamo + timedelta(days=2) if record.fechaprestamo else False

    def generar_prestamo(self):
        self.write({'estado': 'p'})

    def write(self, vals):
        if 'name' not in vals or not vals['name']:
            seq = self.env.ref('biblioteca.sequence_codigo_prestamo').next_by_code('biblioteca.prestamo')
            vals['name'] = seq
        return super(BibliotecaPrestamo, self).write(vals)
    
    def create(self, vals):
        if not vals.get('libro_id'):
            raise ValidationError("Seleccione un libro antes de prestar")
        return super(BibliotecaPrestamo, self).create(vals)

    def generar_prestamo(self):
        print("generando Prestamo")
        self.write({'estado': 'p'})
        
    def devolver(self):
        suma = 1 + 2
        return{
            'type': 'ir.actions.act_window',
            'res_model': 'biblioteca.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('biblioteca.biblioteca_wizard_form').id,
            'context': {'default_prestamo_id': self.id, 'default_observaciones': suma}
        }
            
    @api.depends('fechaprestamo')
    def _compute_fecha_devo(self):
        for record in self:
            if record.fechaprestamo:
                record.fechamax = record.fechaprestamo + timedelta(days=2)
            else:
                record.fechamax = False

#    @api.depends('libro_id', 'usuario_id')
#    def _compute_display_name(self):
#        for record in self:
#            record.display_name = f"{record.libro_id.name or ''} - {record.usuario_id.nombre or ''}"
                        
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
        [('re', 'Retraso'), 
         ('da', 'Daño'), 
         ('pe', 'Pérdida')],
        string='Motivo', required=True
    )
    fecha = fields.Date(string='Fecha', required=True)
    estado = fields.Selection(
        [('pen', 'Pendiente'), 
         ('pa', 'Pagado')],
        string='Estado',required=True, default='pen'
    )
    prestamo = fields.Many2one('biblioteca.prestamo')
    
    @api.constrains('motivo')
    def _motivo(self):
        for record in self:
            motivos = [m.strip() for m in record.motivo.split(',')]
            if 'da' in motivos and 'pe' in motivos:
                raise ValidationError("No puedes seleccionar 'Daño' y 'Pérdida' al mismo tiempo.")