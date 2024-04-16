#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError


classServerActions(models.Model):
    """AddSMSoptioninserveractions."""
    _name='ir.actions.server'
    _inherit=['ir.actions.server']

    state=fields.Selection(selection_add=[
        ('sms','SendSMSTextMessage'),
    ],ondelete={'sms':'cascade'})
    #SMS
    sms_template_id=fields.Many2one(
        'sms.template','SMSTemplate',ondelete='setnull',
        domain="[('model_id','=',model_id)]",
    )
    sms_mass_keep_log=fields.Boolean('LogasNote',default=True)

    @api.constrains('state','model_id')
    def_check_sms_capability(self):
        foractioninself:
            ifaction.state=='sms'andnotaction.model_id.is_mail_thread:
                raiseValidationError(_("SendingSMScanonlybedoneonamail.threadmodel"))

    def_run_action_sms_multi(self,eval_context=None):
        #TDECLEANME:whengoingtonewapiwithserveraction,removeaction
        ifnotself.sms_template_idorself._is_recompute():
            returnFalse

        records=eval_context.get('records')oreval_context.get('record')
        ifnotrecords:
            returnFalse

        composer=self.env['sms.composer'].with_context(
            default_res_model=records._name,
            default_res_ids=records.ids,
            default_composition_mode='mass',
            default_template_id=self.sms_template_id.id,
            default_mass_keep_log=self.sms_mass_keep_log,
        ).create({})
        composer.action_send_sms()
        returnFalse
