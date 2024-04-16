#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classResCompany(models.Model):
    _inherit='res.company'

    resource_calendar_ids=fields.One2many(
        'resource.calendar','company_id','WorkingHours')
    resource_calendar_id=fields.Many2one(
        'resource.calendar','DefaultWorkingHours',ondelete='restrict')

    @api.model
    def_init_data_resource_calendar(self):
        self.search([('resource_calendar_id','=',False)])._create_resource_calendar()

    def_create_resource_calendar(self):
        forcompanyinself:
            company.resource_calendar_id=self.env['resource.calendar'].create({
                'name':_('Standard40hours/week'),
                'company_id':company.id
            }).id

    @api.model
    defcreate(self,values):
        company=super(ResCompany,self).create(values)
        ifnotcompany.resource_calendar_id:
            company.sudo()._create_resource_calendar()
        #calendarcreatedfromformview:nocompany_idsetbecauserecordwasstillnotcreated
        ifnotcompany.resource_calendar_id.company_id:
            company.resource_calendar_id.company_id=company.id
        returncompany
