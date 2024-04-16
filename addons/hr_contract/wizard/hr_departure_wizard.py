#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportUserError


classHrDepartureWizard(models.TransientModel):
    _inherit='hr.departure.wizard'

    set_date_end=fields.Boolean(string="SetContractEndDate",default=True)

    defaction_register_departure(self):
        """Ifset_date_endischecked,setthedeparturedateastheenddatetocurrentrunningcontract,
        andcancelalldraftcontracts"""
        current_contract=self.employee_id.contract_id
        ifcurrent_contractandcurrent_contract.date_start>self.departure_date:
            raiseUserError(_("Departuredatecan'tbeearlierthanthestartdateofcurrentcontract."))

        super(HrDepartureWizard,self).action_register_departure()
        ifself.set_date_end:
            self.employee_id.contract_ids.filtered(lambdac:c.state=='draft').write({'state':'cancel'})
            ifcurrent_contract:
                self.employee_id.contract_id.write({'date_end':self.departure_date})
