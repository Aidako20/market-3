#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classHrPayrollStructureType(models.Model):
    _name='hr.payroll.structure.type'
    _description='ContractType'

    name=fields.Char('ContractType')
    default_resource_calendar_id=fields.Many2one(
        'resource.calendar','DefaultWorkingHours',
        default=lambdaself:self.env.company.resource_calendar_id)
    country_id=fields.Many2one('res.country',string='Country',default=lambdaself:self.env.company.country_id)
