
fromflectraimport_,api,fields,models

classSnailmailLetterCancel(models.TransientModel):
    _name='snailmail.letter.cancel'
    _description='Dismissnotificationforresendbymodel'

    model=fields.Char(string='Model')
    help_message=fields.Char(string='Helpmessage',compute='_compute_help_message')

    @api.depends('model')
    def_compute_help_message(self):
        forwizardinself:
            wizard.help_message=_("Areyousureyouwanttodiscard%ssnailmaildeliveryfailures?Youwon'tbeabletore-sendtheseletterslater!")%(wizard._context.get('unread_counter'))

    defcancel_resend_action(self):
        author_id=self.env.user.id
        forwizardinself:
            letters=self.env['snailmail.letter'].search([
                ('state','notin',['sent','canceled','pending']),
                ('user_id','=',author_id),
                ('model','=',wizard.model)
            ])
            forletterinletters:
                letter.cancel()
        return{'type':'ir.actions.act_window_close'}
