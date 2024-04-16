#-*-coding:utf-8-*-

fromflectraimportfields,models


classNotification(models.Model):
    _inherit='mail.notification'

    notification_type=fields.Selection(selection_add=[('snail','Snailmail')],ondelete={'snail':'cascade'})
    letter_id=fields.Many2one('snailmail.letter',string="SnailmailLetter",index=True,ondelete='cascade')
    failure_type=fields.Selection(selection_add=[
        ('sn_credit',"SnailmailCreditError"),
        ('sn_trial',"SnailmailTrialError"),
        ('sn_price',"SnailmailNoPriceAvailable"),
        ('sn_fields',"SnailmailMissingRequiredFields"),
        ('sn_format',"SnailmailFormatError"),
        ('sn_error',"SnailmailUnknownError"),
    ])
