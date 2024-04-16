#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classAccountChartTemplate(models.Model):
    _inherit='account.chart.template'

    def_prepare_all_journals(self,acc_template_ref,company,journals_dict=None):
        res=super(AccountChartTemplate,self)._prepare_all_journals(acc_template_ref,company,journals_dict=journals_dict)
        ifself==self.env.ref('l10n_in.indian_chart_template_standard'):
            forjournalinres:
                ifjournal.get('type')in('sale','purchase'):
                    journal['l10n_in_gstin_partner_id']=company.partner_id.id
                ifjournal['code']=='INV':
                    journal['name']=_('TaxInvoices')
        returnres

classAccountTaxTemplate(models.Model):
    _inherit='account.tax.template'

    l10n_in_reverse_charge=fields.Boolean("Reversecharge",help="Tickthisifthistaxisreversecharge.OnlyforIndianaccounting")
    
    def_get_tax_vals(self,company,tax_template_to_tax):
        val=super(AccountTaxTemplate,self)._get_tax_vals(company,tax_template_to_tax)
        ifself.tax_group_id:
            val['l10n_in_reverse_charge']=self.l10n_in_reverse_charge
        returnval
