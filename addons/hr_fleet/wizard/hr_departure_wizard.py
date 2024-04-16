#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classHrDepartureWizard(models.TransientModel):
    _inherit='hr.departure.wizard'

    release_campany_car=fields.Boolean("ReleaseCompanyCar",default=True)

    defaction_register_departure(self):
        super(HrDepartureWizard,self).action_register_departure()
        ifself.release_campany_car:
            self._free_campany_car()

    def_free_campany_car(self):
        """Findallfleet.vehichle.assignation.logrecordsthatlinktotheemployee,ifthereisno
        enddateorenddate>departuredate,updatethedate.Alsocheckfleet.vehicletoseeif
        thereisanyrecordwithitsdirver_idtobetheemployee,setthemtoFalse."""
        drivers=self.employee_id.user_id.partner_id|self.employee_id.sudo().address_home_id
        assignations=self.env['fleet.vehicle.assignation.log'].search([('driver_id','in',drivers.ids)])
        forassignationinassignations:
            ifself.departure_dateand(notassignation.date_endorassignation.date_end>self.departure_date):
                assignation.write({'date_end':self.departure_date})
        cars=self.env['fleet.vehicle'].search([('driver_id','in',drivers.ids)])
        cars.write({'driver_id':False})
