#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMailNotification(models.Model):
    _inherit='mail.notification'

    notification_type=fields.Selection(selection_add=[
        ('sms','SMS')
    ],ondelete={'sms':'setdefault'})
    sms_id=fields.Many2one('sms.sms',string='SMS',index=True,ondelete='setnull')
    sms_number=fields.Char('SMSNumber')
    failure_type=fields.Selection(selection_add=[
        ('sms_number_missing','MissingNumber'),
        ('sms_number_format','WrongNumberFormat'),
        ('sms_credit','InsufficientCredit'),
        ('sms_server','ServerError'),
        ('sms_acc','UnregisteredAccount')
    ])
