#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classChannel(models.Model):
    _inherit='mail.channel'

    subscription_department_ids=fields.Many2many(
        'hr.department',string='HRDepartments',
        help='Automaticallysubscribemembersofthosedepartmentstothechannel.')

    def_subscribe_users(self):
        """Auto-subscribemembersofadepartmenttoachannel"""
        super(Channel,self)._subscribe_users()
        formail_channelinself:
            ifmail_channel.subscription_department_ids:
                mail_channel.write(
                    {'channel_partner_ids':
                        [(4,partner_id)forpartner_idinmail_channel.mapped('subscription_department_ids.member_ids.user_id.partner_id').ids]})

    defwrite(self,vals):
        res=super(Channel,self).write(vals)
        ifvals.get('subscription_department_ids'):
            self._subscribe_users()
        returnres
