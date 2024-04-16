#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classHrDepartureWizard(models.TransientModel):
    _name='hr.departure.wizard'
    _description='DepartureWizard'

    departure_reason=fields.Selection([
        ('fired','Fired'),
        ('resigned','Resigned'),
        ('retired','Retired')
    ],string="DepartureReason",default="fired")
    departure_description=fields.Text(string="AdditionalInformation")
    departure_date=fields.Date(string="DepartureDate",required=True,default=fields.Date.today)
    employee_id=fields.Many2one(
        'hr.employee',string='Employee',required=True,
        default=lambdaself:self.env.context.get('active_id',None),
    )
    archive_private_address=fields.Boolean('ArchivePrivateAddress',default=True)

    defaction_register_departure(self):
        employee=self.employee_id
        employee.departure_reason=self.departure_reason
        employee.departure_description=self.departure_description
        employee.departure_date=self.departure_date

        ifself.archive_private_address:
            #ignorecontactlinkstointernalusers
            private_address=employee.address_home_id
            ifprivate_addressandprivate_address.activeandnotself.env['res.users'].search([('partner_id','=',private_address.id)]):
                private_address.toggle_active()
