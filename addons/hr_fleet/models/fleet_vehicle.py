#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classFleetVehicle(models.Model):
    _inherit='fleet.vehicle'

    mobility_card=fields.Char(compute='_compute_mobility_card',store=True)

    @api.depends('driver_id')
    def_compute_mobility_card(self):
        forvehicleinself:
            employee=self.env['hr.employee']
            ifvehicle.driver_id:
                employee=employee.search([('address_home_id','=',vehicle.driver_id.id)],limit=1)
                ifnotemployee:
                    employee=employee.search([('user_id.partner_id','=',vehicle.driver_id.id)],limit=1)
            vehicle.mobility_card=employee.mobility_card

classHrEmployee(models.Model):
    _inherit="hr.employee"

    defwrite(self,vals):
        res=super().write(vals)
        if'mobility_card'invals:
            vehicles=self.env['fleet.vehicle'].search([('driver_id','in',(self.user_id.partner_id|self.sudo().address_home_id).ids)])
            vehicles._compute_mobility_card()
        returnres
