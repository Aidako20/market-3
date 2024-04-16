#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,exceptions,fields,models,_
fromflectra.addons.phone_validation.toolsimportphone_validation


classMassSMSTest(models.TransientModel):
    _name='mailing.sms.test'
    _description='TestSMSMailing'

    def_default_numbers(self):
        returnself.env.user.partner_id.phone_sanitizedor""

    numbers=fields.Char(string='Number(s)',required=True,
                          default=_default_numbers,help='Comma-separatedlistofphonenumbers')
    mailing_id=fields.Many2one('mailing.mailing',string='Mailing',required=True,ondelete='cascade')

    defaction_send_sms(self):
        self.ensure_one()
        numbers=[number.strip()fornumberinself.numbers.split(',')]
        sanitize_res=phone_validation.phone_sanitize_numbers_w_record(numbers,self.env.user)
        sanitized_numbers=[info['sanitized']forinfoinsanitize_res.values()ifinfo['sanitized']]
        invalid_numbers=[numberfornumber,infoinsanitize_res.items()ifinfo['code']]
        ifinvalid_numbers:
            raiseexceptions.UserError(_('Followingnumbersarenotcorrectlyencoded:%s,example:"+32495858577,+33545555555"',repr(invalid_numbers)))
        
        record=self.env[self.mailing_id.mailing_model_real].search([],limit=1)
        body=self.mailing_id.body_plaintext
        ifrecord:
            #Returnsapropererrorifthereisasyntaxerrorwithjinja
            body=self.env['mail.render.mixin']._render_template(body,self.mailing_id.mailing_model_real,record.ids)[record.id]

        self.env['sms.api']._send_sms_batch([{
            'res_id':0,
            'number':number,
            'content':body,
        }fornumberinsanitized_numbers])
        returnTrue
