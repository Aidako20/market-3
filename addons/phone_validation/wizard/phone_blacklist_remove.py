#-*-coding:utf-8-*-

fromflectraimportfields,models


classPhoneBlacklistRemove(models.TransientModel):
    _name='phone.blacklist.remove'
    _description='Removephonefromblacklist'

    phone=fields.Char(string="PhoneNumber",readonly=True,required=True)
    reason=fields.Char(name="Reason")

    defaction_unblacklist_apply(self):
        returnself.env['phone.blacklist'].action_remove_with_reason(self.phone,self.reason)
