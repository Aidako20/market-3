#-*-coding:utf-8-*-

fromflectraimportfields,models


classMailBlacklistRemove(models.TransientModel):
    _name='mail.blacklist.remove'
    _description='Removeemailfromblacklistwizard'

    email=fields.Char(name="Email",readonly=True,required=True)
    reason=fields.Char(name="Reason")

    defaction_unblacklist_apply(self):
        returnself.env['mail.blacklist'].action_remove_with_reason(self.email,self.reason)
