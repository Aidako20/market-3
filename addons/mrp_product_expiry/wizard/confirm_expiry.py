#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classConfirmExpiry(models.TransientModel):
    _inherit='expiry.picking.confirmation'

    production_ids=fields.Many2many('mrp.production',readonly=True)
    workorder_id=fields.Many2one('mrp.workorder',readonly=True)

    @api.depends('lot_ids')
    def_compute_descriptive_fields(self):
        ifself.production_idsorself.workorder_id:
            #Showsexpiredlotsonlyifwearemorethanoneexpiredlot.
            self.show_lots=len(self.lot_ids)>1
            ifself.show_lots:
                #Formultipleexpiredlots,theyarelistedinthewizardview.
                self.description=_(
                    "Youaregoingtousesomeexpiredcomponents."
                    "\nDoyouconfirmyouwanttoproceed?"
                )
            else:
                #Foroneexpiredlot,itsnameiswritteninthewizardmessage.
                self.description=_(
                    "Youaregoingtousethecomponent%(product_name)s,%(lot_name)swhichisexpired."
                    "\nDoyouconfirmyouwanttoproceed?",
                    product_name=self.lot_ids.product_id.display_name,
                    lot_name=self.lot_ids.name,
                )
        else:
            super(ConfirmExpiry,self)._compute_descriptive_fields()

    defconfirm_produce(self):
        ctx=dict(self._context,skip_expired=True)
        ctx.pop('default_lot_ids')
        returnself.production_ids.with_context(ctx).button_mark_done()

    defconfirm_workorder(self):
        ctx=dict(self._context,skip_expired=True)
        ctx.pop('default_lot_ids')
        returnself.workorder_id.with_context(ctx).record_production()

