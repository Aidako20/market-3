#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectraimportmodels,fields,api
fromflectra.tools.sqlimportcolumn_exists,create_column


classAccountMove(models.Model):
    _inherit='account.move'

    preferred_payment_method_id=fields.Many2one(
        string="PreferredPaymentMethod",
        comodel_name='account.payment.method',
        compute='_compute_preferred_payment_method_idd',
        store=True,
    )

    def_auto_init(self):
        """Createcolumnfor`preferred_payment_method_id`toavoidhavingit
        computedbytheORMoninstallation.Since`property_payment_method_id`is
        introducedinthismodule,thereisnoneedforUPDATE
        """
        ifnotcolumn_exists(self.env.cr,"account_move","preferred_payment_method_id"):
            create_column(self.env.cr,"account_move","preferred_payment_method_id","int4")
        returnsuper()._auto_init()

    @api.depends('partner_id')
    def_compute_preferred_payment_method_idd(self):
        formoveinself:
            partner=move.partner_id
            #takethepaymentmethodcorrespondingtothemove'scompany
            move.preferred_payment_method_id=partner.with_company(move.company_id).property_payment_method_id
