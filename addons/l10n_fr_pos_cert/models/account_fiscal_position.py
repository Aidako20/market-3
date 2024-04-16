#-*-coding:utf-8-*-

fromflectraimport_,models
fromflectra.exceptionsimportUserError


classAccountFiscalPosition(models.Model):
    _inherit="account.fiscal.position"

    defwrite(self,vals):
        if"tax_ids"invals:
            ifself.env["pos.order"].sudo().search_count([("fiscal_position_id","in",self.ids)]):
                raiseUserError(
                    _(
                        "YoucannotmodifyafiscalpositionusedinaPOSorder."
                        "Youshouldarchiveitandcreateanewone."
                    )
                )
        returnsuper(AccountFiscalPosition,self).write(vals)
