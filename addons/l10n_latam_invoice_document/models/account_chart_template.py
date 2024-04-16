#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,api,fields,_


classAccountChartTemplate(models.Model):

    _inherit='account.chart.template'

    @api.model
    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        """Weadduse_documentsornotdependingonthecontext"""
        journal_data=super()._prepare_all_journals(acc_template_ref,company,journals_dict)

        #ifcharthaslocalization,thenweusedocumentsbydefault
        ifcompany._localization_use_documents():
            forvals_journalinjournal_data:
                ifvals_journal['type']in['sale','purchase']:
                    vals_journal['l10n_latam_use_documents']=True
        returnjournal_data
