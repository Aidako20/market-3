#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    @api.model
    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        journal_data=super(AccountChartTemplate,self)._prepare_all_journals(
            acc_template_ref,company,journals_dict)
        forjournalinjournal_data:
            ifjournal['type']in('sale','purchase')andcompany.country_id.code=="BE":
                journal.update({'refund_sequence':True})
        returnjournal_data
