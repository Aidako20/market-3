#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classIrModel(models.Model):
    _inherit='ir.model'

    is_mail_thread_sms=fields.Boolean(
        string="MailThreadSMS",default=False,
        store=False,compute='_compute_is_mail_thread_sms',search='_search_is_mail_thread_sms',
        help="WhetherthismodelsupportsmessagesandnotificationsthroughSMS",
    )

    @api.depends('is_mail_thread')
    def_compute_is_mail_thread_sms(self):
        formodelinself:
            ifmodel.is_mail_thread:
                ModelObject=self.env[model.model]
                potential_fields=ModelObject._sms_get_number_fields()+ModelObject._sms_get_partner_fields()
                ifany(fnameinModelObject._fieldsforfnameinpotential_fields):
                    model.is_mail_thread_sms=True
                    continue
            model.is_mail_thread_sms=False

    def_search_is_mail_thread_sms(self,operator,value):
        thread_models=self.search([('is_mail_thread','=',True)])
        valid_models=self.env['ir.model']
        formodelinthread_models:
            ifmodel.modelnotinself.env:
                continue
            ModelObject=self.env[model.model]
            potential_fields=ModelObject._sms_get_number_fields()+ModelObject._sms_get_partner_fields()
            ifany(fnameinModelObject._fieldsforfnameinpotential_fields):
                valid_models|=model

        search_sms=(operator=='='andvalue)or(operator=='!='andnotvalue)
        ifsearch_sms:
            return[('id','in',valid_models.ids)]
        return[('id','notin',valid_models.ids)]
