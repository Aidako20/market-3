#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classMrpWorkorder(models.Model):
    _inherit='mrp.production'

    def_pre_button_mark_done(self):
        confirm_expired_lots=self._check_expired_lots()
        ifconfirm_expired_lots:
            returnconfirm_expired_lots
        returnsuper()._pre_button_mark_done()

    def_check_expired_lots(self):
        #Weusethe'skip_expired'contextkeytoavoidtomakethecheckwhen
        #useralreadyconfirmedthewizardaboutusingexpiredlots.
        ifself.env.context.get('skip_expired'):
            returnFalse
        expired_lot_ids=self.move_raw_ids.move_line_ids.filtered(lambdaml:ml.lot_id.product_expiry_alert).lot_id.ids
        ifexpired_lot_ids:
            return{
                'name':_('Confirmation'),
                'type':'ir.actions.act_window',
                'res_model':'expiry.picking.confirmation',
                'view_mode':'form',
                'target':'new',
                'context':self._get_expired_context(expired_lot_ids),
            }

    def_get_expired_context(self,expired_lot_ids):
        context=dict(self.env.context)
        context.update({
            'default_lot_ids':[(6,0,expired_lot_ids)],
            'default_production_ids':self.ids,
        })
        returncontext
