#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classEmployee(models.Model):
    _inherit=["hr.employee"]

    subordinate_ids=fields.One2many('hr.employee',string='Subordinates',compute='_compute_subordinates',help="Directandindirectsubordinates",
                                      compute_sudo=True)


classHrEmployeePublic(models.Model):
    _inherit=["hr.employee.public"]

    subordinate_ids=fields.One2many('hr.employee.public',string='Subordinates',compute='_compute_subordinates',help="Directandindirectsubordinates",
                                      compute_sudo=True)
