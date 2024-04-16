#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMailPerformanceThread(models.Model):
    _name='mail.performance.thread'
    _description='Performance:mail.thread'
    _inherit=['mail.thread']

    name=fields.Char()
    value=fields.Integer()
    value_pc=fields.Float(compute="_value_pc",store=True)
    track=fields.Char(default='test',tracking=True)
    partner_id=fields.Many2one('res.partner',string='Customer')

    @api.depends('value')
    def_value_pc(self):
        forrecordinself:
            record.value_pc=float(record.value)/100


classMailPerformanceTracking(models.Model):
    _name='mail.performance.tracking'
    _description='Performance:multitracking'
    _inherit=['mail.thread']

    name=fields.Char(required=True,tracking=True)
    field_0=fields.Char(tracking=True)
    field_1=fields.Char(tracking=True)
    field_2=fields.Char(tracking=True)


classMailTestFieldType(models.Model):
    """Testdefaultvalues,notablytype,messingthroughmodelsduringgateway
    processing(i.e.lead.typeversusattachment.type)."""
    _description='TestFieldType'
    _name='mail.test.field.type'
    _inherit=['mail.thread']

    name=fields.Char()
    email_from=fields.Char()
    datetime=fields.Datetime(default=fields.Datetime.now)
    customer_id=fields.Many2one('res.partner','Customer')
    type=fields.Selection([('first','First'),('second','Second')])
    user_id=fields.Many2one('res.users','Responsible',tracking=True)

    @api.model_create_multi
    defcreate(self,vals_list):
        #Emulateanaddonthataltersthecreationcontext,suchas`crm`
        ifnotself._context.get('default_type'):
            self=self.with_context(default_type='first')
        returnsuper(MailTestFieldType,self).create(vals_list)


classMailTestTrackCompute(models.Model):
    _name='mail.test.track.compute'
    _description="Testtrackingwithcomputedfields"
    _inherit=['mail.thread']

    partner_id=fields.Many2one('res.partner',tracking=True)
    partner_name=fields.Char(related='partner_id.name',store=True,tracking=True)
    partner_email=fields.Char(related='partner_id.email',store=True,tracking=True)
    partner_phone=fields.Char(related='partner_id.phone',tracking=True)


classMailTestMultiCompany(models.Model):
    """Thismodelcanbeusedinmulticompanytests"""
    _name='mail.test.multi.company'
    _description="TestMultiCompanyMail"
    _inherit='mail.thread'

    name=fields.Char()
    company_id=fields.Many2one('res.company')

classMailTestMultiCompanyWithActivity(models.Model):
    """Thismodelcanbeusedinmulticompanytestswithactivity"""
    _name="mail.test.multi.company.with.activity"
    _description="TestMultiCompanyMailWithActivity"
    _inherit=["mail.thread","mail.activity.mixin"]

    name=fields.Char()
    company_id=fields.Many2one("res.company")


classMailTestSelectionTracking(models.Model):
    """Testtrackingforselectionfields"""
    _description='TestSelectionTracking'
    _name='mail.test.track.selection'
    _inherit=['mail.thread']

    name=fields.Char()
    type=fields.Selection([('first','First'),('second','Second')],tracking=True)
