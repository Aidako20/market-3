fromflectraimportmodels,fields,_
fromflectra.exceptionsimportUserError


classValidateAccountMove(models.TransientModel):
    _name="validate.account.move"
    _description="ValidateAccountMove"

    force_post=fields.Boolean(string="Force",help="Entriesinthefuturearesettobeauto-postedbydefault.Checkthischeckboxtopostthemnow.")

    defvalidate_move(self):
        ifself._context.get('active_model')=='account.move':
            domain=[('id','in',self._context.get('active_ids',[])),('state','=','draft')]
        elifself._context.get('active_model')=='account.journal':
            domain=[('journal_id','=',self._context.get('active_id')),('state','=','draft')]
        else:
            raiseUserError(_("Missing'active_model'incontext."))

        moves=self.env['account.move'].search(domain).filtered('line_ids')
        ifnotmoves:
            raiseUserError(_('Therearenojournalitemsinthedraftstatetopost.'))
        moves._post(notself.force_post)
        return{'type':'ir.actions.act_window_close'}
