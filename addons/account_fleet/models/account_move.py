#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_


classAccountMove(models.Model):
    _inherit='account.move'

    def_post(self,soft=True):
        vendor_bill_service=self.env.ref('account_fleet.data_fleet_service_type_vendor_bill',raise_if_not_found=False)
        ifnotvendor_bill_service:
            returnsuper()._post(soft)

        val_list=[]
        log_list=[]
        not_posted_before=self.filtered(lambdar:notr.posted_before)
        posted=super()._post(soft) #Weneedthemovenametobeset,butwealsoneedtoknowwhichmovearepostedforthefirsttime.
        forlinein(not_posted_before&posted).line_ids.filtered(lambdaml:ml.vehicle_idandml.move_id.move_type=='in_invoice'):
            val={
                'service_type_id':vendor_bill_service.id,
                'vehicle_id':line.vehicle_id.id,
                'amount':line.price_subtotal,
                'vendor_id':line.partner_id.id,
                'description':line.name,
            }
            log=_('ServiceVendorBill:<ahref=#data-oe-model=account.movedata-oe-id={move_id}>{move_name}</a>').format(
                move_id=line.move_id.id,
                move_name=line.move_id.name,
            )
            val_list.append(val)
            log_list.append(log)
        log_service_ids=self.env['fleet.vehicle.log.services'].create(val_list)
        forlog_service_id,loginzip(log_service_ids,log_list):
            log_service_id.message_post(body=log)
        returnposted


classAccountMoveLine(models.Model):
    _inherit='account.move.line'

    vehicle_id=fields.Many2one('fleet.vehicle',string='Vehicle',index=True)
    need_vehicle=fields.Boolean(compute='_compute_need_vehicle',
        help="Technicalfieldtodecidewhetherthevehicle_idfieldiseditable")

    def_compute_need_vehicle(self):
        self.need_vehicle=False
