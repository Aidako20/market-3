#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSaleOrder(models.Model):
    _inherit="sale.order"

    l10n_in_reseller_partner_id=fields.Many2one('res.partner',
        string='Reseller',domain="[('vat','!=',False),'|',('company_id','=',False),('company_id','=',company_id)]",readonly=True,states={'draft':[('readonly',False)],'sent':[('readonly',False)]})
    l10n_in_journal_id=fields.Many2one('account.journal',string="Journal",compute="_compute_l10n_in_journal_id",store=True,readonly=True,states={'draft':[('readonly',False)],'sent':[('readonly',False)]})
    l10n_in_gst_treatment=fields.Selection([
            ('regular','RegisteredBusiness-Regular'),
            ('composition','RegisteredBusiness-Composition'),
            ('unregistered','UnregisteredBusiness'),
            ('consumer','Consumer'),
            ('overseas','Overseas'),
            ('special_economic_zone','SpecialEconomicZone'),
            ('deemed_export','DeemedExport'),
        ],string="GSTTreatment",readonly=True,states={'draft':[('readonly',False)],'sent':[('readonly',False)]},compute="_compute_l10n_in_gst_treatment",store=True)
    l10n_in_company_country_code=fields.Char(related='company_id.country_id.code',string="Countrycode")

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

    @api.depends('company_id')
    def_compute_l10n_in_journal_id(self):
        fororderinself:
            #setdefaultvalueasFalsesoCacheMisserrorneveroccursforthisfield.
            order.l10n_in_journal_id=False
            iforder.l10n_in_company_country_code=='IN':
                domain=[('company_id','=',order.company_id.id),('type','=','sale')]
                journal=self.env['account.journal'].search(domain,limit=1)
                ifjournal:
                    order.l10n_in_journal_id=journal.id


    def_prepare_invoice(self):
        invoice_vals=super(SaleOrder,self)._prepare_invoice()
        ifself.l10n_in_company_country_code=='IN':
            invoice_vals['l10n_in_reseller_partner_id']=self.l10n_in_reseller_partner_id.id
            ifself.l10n_in_journal_id:
                invoice_vals['journal_id']=self.l10n_in_journal_id.id
            invoice_vals['l10n_in_gst_treatment']=self.l10n_in_gst_treatment
        returninvoice_vals
