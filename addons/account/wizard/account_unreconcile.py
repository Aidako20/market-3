fromflectraimportmodels,api


classAccountUnreconcile(models.TransientModel):
    _name="account.unreconcile"
    _description="AccountUnreconcile"

    deftrans_unrec(self):
        context=dict(self._contextor{})
        ifcontext.get('active_ids',False):
            self.env['account.move.line'].browse(context.get('active_ids')).remove_move_reconcile()
        return{'type':'ir.actions.act_window_close'}
