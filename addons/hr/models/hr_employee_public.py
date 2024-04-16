#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classHrEmployeePublic(models.Model):
    _name="hr.employee.public"
    _inherit=["hr.employee.base"]
    _description='PublicEmployee'
    _order='name'
    _auto=False
    _log_access=True#Includemagicfields

    #Fieldscomingfromhr.employee.base
    create_date=fields.Datetime(readonly=True)
    name=fields.Char(readonly=True)
    active=fields.Boolean(readonly=True)
    department_id=fields.Many2one(readonly=True)
    job_id=fields.Many2one(readonly=True)
    job_title=fields.Char(readonly=True)
    company_id=fields.Many2one(readonly=True)
    address_id=fields.Many2one(readonly=True)
    mobile_phone=fields.Char(readonly=True)
    work_phone=fields.Char(readonly=True)
    work_email=fields.Char(readonly=True)
    work_location=fields.Char(readonly=True)
    user_id=fields.Many2one(readonly=True)
    resource_id=fields.Many2one(readonly=True)
    resource_calendar_id=fields.Many2one(readonly=True)
    tz=fields.Selection(readonly=True)
    color=fields.Integer(readonly=True)

    #hr.employee.publicspecificfields
    child_ids=fields.One2many('hr.employee.public','parent_id',string='Directsubordinates',readonly=True)
    image_1920=fields.Image("OriginalImage",compute='_compute_image',compute_sudo=True)
    image_1024=fields.Image("Image1024",compute='_compute_image',compute_sudo=True)
    image_512=fields.Image("Image512",compute='_compute_image',compute_sudo=True)
    image_256=fields.Image("Image256",compute='_compute_image',compute_sudo=True)
    image_128=fields.Image("Image128",compute='_compute_image',compute_sudo=True)
    parent_id=fields.Many2one('hr.employee.public','Manager',readonly=True)
    coach_id=fields.Many2one('hr.employee.public','Coach',readonly=True)
    user_partner_id=fields.Many2one(related='user_id.partner_id',related_sudo=False,string="User'spartner")

    def_compute_image(self):
        foremployeeinself:
            #Wehavetobeinsudotohaveaccesstotheimages
            employee_id=self.sudo().env['hr.employee'].browse(employee.id)
            employee.image_1920=employee_id.image_1920
            employee.image_1024=employee_id.image_1024
            employee.image_512=employee_id.image_512
            employee.image_256=employee_id.image_256
            employee.image_128=employee_id.image_128

    @api.model
    def_get_fields(self):
        return','.join('emp.%s'%nameforname,fieldinself._fields.items()iffield.storeandfield.typenotin['many2many','one2many'])

    definit(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute("""CREATEorREPLACEVIEW%sas(
            SELECT
                %s
            FROMhr_employeeemp
        )"""%(self._table,self._get_fields()))
