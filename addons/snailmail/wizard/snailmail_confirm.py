#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classSnailmailConfirm(models.AbstractModel):
    _name='snailmail.confirm'
    _description='SnailmailConfirm'

    model_name=fields.Char()

    @api.model
    defshow_warning(self):
        returnnotself.env['ir.config_parameter'].sudo().get_param('%s.warning_shown'%self._name,False)

    defaction_open(self):
        view=self.env.ref('snailmail.snailmail_confirm_view')
        return{
            'name':_('Snailmail'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':self._name,
            'views':[(view.id,'form')],
            'view_id':view.id,
            'target':'new',
            'res_id':self.id,
            'context':self.env.context
        }

    defaction_confirm(self):
        self.env['ir.config_parameter'].sudo().set_param('%s.warning_shown'%self._name,True)
        self._confirm()
        returnself._continue()

    defaction_cancel(self):
        self.env['ir.config_parameter'].sudo().set_param('%s.warning_shown'%self._name,True)
        returnself._continue()

    """
    Calledwhethertheuserconfirmsorcancelspostingtheletter,e.g.tocontinuetheaction
    """
    def_continue(self):
        pass

    """
    Calledonlywhentheuserconfirmssendingtheletter
    """
    def_confirm(self):
        pass
