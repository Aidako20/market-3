#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models,api,_


classResPartner(models.Model):
    _inherit='res.partner'

    siret=fields.Char(string='SIRET',size=14)

classChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        journals=super(ChartTemplate,self)._prepare_all_journals(acc_template_ref,company,journals_dict)
        ifcompany.country_id.code=="FR":
            #ForFrance,sale/purchasejournalsmusthaveadedicatedsequenceforrefunds
            forjournalinjournals:
                ifjournal['type']in['sale','purchase']:
                    journal['refund_sequence']=True
        returnjournals
