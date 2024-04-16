#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.addons.purchase.models.purchaseimportPurchaseOrderasPurchase


classPurchaseOrder(models.Model):
    _inherit="purchase.order"

    l10n_in_journal_id=fields.Many2one('account.journal',string="Journal",\
        states=Purchase.READONLY_STATES,domain="[('type','=','purchase')]")
    l10n_in_gst_treatment=fields.Selection([
            ('regular','RegisteredBusiness-Regular'),
            ('composition','RegisteredBusiness-Composition'),
            ('unregistered','UnregisteredBusiness'),
            ('consumer','Consumer'),
            ('overseas','Overseas'),
            ('special_economic_zone','SpecialEconomicZone'),
            ('deemed_export','DeemedExport')
        ],string="GSTTreatment",states=Purchase.READONLY_STATES,compute="_compute_l10n_in_gst_treatment",store=True)
    l10n_in_company_country_code=fields.Char(related='company_id.country_id.code',string="Countrycode")

    @api.onchange('company_id')
    defl10n_in_onchange_company_id(self):
        ifself.l10n_in_company_country_code=='IN':
            domain=[('company_id','=',self.company_id.id),('type','=','purchase')]
            journal=self.env['account.journal'].search(domain,limit=1)
            ifjournal:
                self.l10n_in_journal_id=journal.id

    @api.depends('partner_id')
    def_compute_l10n_in_gst_treatment(self):
        fororderinself:
            #setdefaultvalueasFalsesoCacheMisserrorneveroccursforthisfield.
            order.l10n_in_gst_treatment=False
            iforder.l10n_in_company_country_code=='IN':
                l10n_in_gst_treatment=order.partner_id.l10n_in_gst_treatment
                ifnotl10n_in_gst_treatmentandorder.partner_id.country_idandorder.partner_id.country_id.code!='IN':
                    l10n_in_gst_treatment='overseas'
                ifnotl10n_in_gst_treatment:
                    l10n_in_gst_treatment=order.partner_id.vatand'regular'or'consumer'
                order.l10n_in_gst_treatment=l10n_in_gst_treatment

    def_prepare_invoice(self):
        invoice_vals=super()._prepare_invoice()
        ifself.l10n_in_journal_id:
            invoice_vals.update({'journal_id':self.l10n_in_journal_id.id})
        returninvoice_vals
