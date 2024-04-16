#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classStockPicking(models.Model):
    _inherit="stock.picking"

    def_pre_action_done_hook(self):
        res=super()._pre_action_done_hook()
        #Weusethe'skip_expired'contextkeytoavoidtomakethecheckwhen
        #userdidalreadyconfirmedthewizardaboutexpiredlots.
        ifresisTrueandnotself.env.context.get('skip_expired'):
            pickings_to_warn_expired=self._check_expired_lots()
            ifpickings_to_warn_expired:
                returnpickings_to_warn_expired._action_generate_expired_wizard()
        returnres

    def_check_expired_lots(self):
        expired_pickings=self.move_line_ids.filtered(lambdaml:ml.lot_id.product_expiry_alert).picking_id
        returnexpired_pickings

    def_action_generate_expired_wizard(self):
        expired_lot_ids=self.move_line_ids.filtered(lambdaml:ml.lot_id.product_expiry_alert).lot_id.ids
        view_id=self.env.ref('product_expiry.confirm_expiry_view').id
        context=dict(self.env.context)

        context.update({
            'default_picking_ids':[(6,0,self.ids)],
            'default_lot_ids':[(6,0,expired_lot_ids)],
        })
        return{
            'name':_('Confirmation'),
            'type':'ir.actions.act_window',
            'res_model':'expiry.picking.confirmation',
            'view_mode':'form',
            'views':[(view_id,'form')],
            'view_id':view_id,
            'target':'new',
            'context':context,
        }
