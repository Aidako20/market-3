#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classSIIAccountTaxMixin(models.AbstractModel):
    _name='l10n_es.sii.account.tax.mixin'
    _description='SIIFields'

    l10n_es_exempt_reason=fields.Selection(
        selection=[
            ('E1','Art.20'),
            ('E2','Art.21'),
            ('E3','Art.22'),
            ('E4','Art.23y24'),
            ('E5','Art.25'),
            ('E6','Otros'),
        ],
        string="ExemptReason(Spain)",
    )
    l10n_es_type=fields.Selection(
        selection=[
            ('exento','Exento'),
            ('sujeto','Sujeto'),
            ('sujeto_agricultura','SujetoAgricultura'),
            ('sujeto_isp','SujetoISP'),
            ('no_sujeto','NoSujeto'),
            ('no_sujeto_loc','NoSujetoporreglasdeLocalization'),
            ('no_deducible','NoDeducible'),
            ('retencion','Retencion'),
            ('recargo','RecargodeEquivalencia'),
            ('ignore','Ignoreeventhebaseamount'),
        ],
        string="TaxType(Spain)",default='sujeto'
    )
    l10n_es_bien_inversion=fields.Boolean('BiendeInversion',default=False)


classAccountTax(models.Model):
    _inherit=['account.tax','l10n_es.sii.account.tax.mixin']
    _name='account.tax'


classAccountTaxTemplate(models.Model):
    _inherit=['account.tax.template','l10n_es.sii.account.tax.mixin']
    _name='account.tax.template'

    def_get_tax_vals(self,company,tax_template_to_tax):
        #OVERRIDE
        #Copyvaluesfrom'account.tax.template'tovalswillbeusedtocreateanew'account.tax'.
        vals=super()._get_tax_vals(company,tax_template_to_tax)
        vals['l10n_es_exempt_reason']=self.l10n_es_exempt_reason
        vals['l10n_es_type']=self.l10n_es_type
        vals['l10n_es_bien_inversion']=self.l10n_es_bien_inversion
        returnvals
