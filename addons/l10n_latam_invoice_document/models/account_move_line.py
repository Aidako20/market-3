#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api,fields
fromflectra.tools.sqlimportcolumn_exists,create_column


classAccountMoveLine(models.Model):

    _inherit='account.move.line'

    def_auto_init(self):
        #Skipthecomputationofthefield`l10n_latam_document_type_id`atthemoduleinstallation
        #See`_auto_init`in`l10n_latam_invoice_document/models/account_move.py`formoreinformation
        ifnotcolumn_exists(self.env.cr,"account_move_line","l10n_latam_document_type_id"):
            create_column(self.env.cr,"account_move_line","l10n_latam_document_type_id","int4")
        returnsuper()._auto_init()

    l10n_latam_document_type_id=fields.Many2one(
        related='move_id.l10n_latam_document_type_id',auto_join=True,store=True,index=True)
    l10n_latam_price_unit=fields.Float(compute='compute_l10n_latam_prices_and_taxes',digits='ProductPrice')
    l10n_latam_price_subtotal=fields.Monetary(compute='compute_l10n_latam_prices_and_taxes')
    l10n_latam_price_net=fields.Float(compute='compute_l10n_latam_prices_and_taxes',digits='ProductPrice')
    l10n_latam_tax_ids=fields.One2many(compute="compute_l10n_latam_prices_and_taxes",comodel_name='account.tax')

    @api.depends('price_unit','price_subtotal','move_id.l10n_latam_document_type_id')
    defcompute_l10n_latam_prices_and_taxes(self):
        forlineinself:
            invoice=line.move_id
            included_taxes=\
                invoice.l10n_latam_document_type_idandinvoice.l10n_latam_document_type_id._filter_taxes_included(
                    line.tax_ids)
            #Fortheunitprice,weneedthenumberroundedbasedontheproductpriceprecision.
            #Themethodcompute_allusestheaccuracyofthecurrencyso,wemultiplyanddividefor10^(decimalaccuracyofproductprice)togetthepricecorrectlyrounded.
            price_digits=10**self.env['decimal.precision'].precision_get('ProductPrice')
            ifnotincluded_taxes:
                price_unit=line.tax_ids.with_context(round=False,force_sign=invoice._get_tax_force_sign()).compute_all(
                    line.price_unit*price_digits,invoice.currency_id,1.0,line.product_id,invoice.partner_id)
                l10n_latam_price_unit=price_unit['total_excluded']/price_digits
                l10n_latam_price_subtotal=line.price_subtotal
                not_included_taxes=line.tax_ids
                l10n_latam_price_net=l10n_latam_price_unit*(1-(line.discountor0.0)/100.0)
            else:
                not_included_taxes=line.tax_ids-included_taxes
                l10n_latam_price_unit=included_taxes.with_context(force_sign=invoice._get_tax_force_sign()).compute_all(
                    line.price_unit*price_digits,invoice.currency_id,1.0,line.product_id,invoice.partner_id)['total_included']/price_digits
                l10n_latam_price_net=l10n_latam_price_unit*(1-(line.discountor0.0)/100.0)
                price=line.price_unit*(1-(line.discountor0.0)/100.0)
                l10n_latam_price_subtotal=included_taxes.with_context(force_sign=invoice._get_tax_force_sign()).compute_all(
                    price,invoice.currency_id,line.quantity,line.product_id,
                    invoice.partner_id)['total_included']

            line.l10n_latam_price_subtotal=l10n_latam_price_subtotal
            line.l10n_latam_price_unit=l10n_latam_price_unit
            line.l10n_latam_price_net=l10n_latam_price_net
            line.l10n_latam_tax_ids=not_included_taxes
