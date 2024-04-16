#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectraimporttools


classAccountJournal(models.Model):
    _inherit="account.journal"

    #Useforfilterimportandexporttype.
    l10n_in_gstin_partner_id=fields.Many2one('res.partner',string="GSTINUnit",ondelete="restrict",help="GSTINrelatedtothisjournal.IfemptythenconsiderascompanyGSTIN.")

    defname_get(self):
        """
            AddGSTINnumberinnameassuffixsousercaneasilyfindtherightjournal.
            Usedsupertoensurenothingismissed.
        """
        result=super().name_get()
        result_dict=dict(result)
        indian_journals=self.filtered(lambdaj:j.company_id.country_id.code=='IN'and
            j.l10n_in_gstin_partner_idandj.l10n_in_gstin_partner_id.vat)
        forjournalinindian_journals:
            name=result_dict[journal.id]
            name+="-%s"%(journal.l10n_in_gstin_partner_id.vat)
            result_dict[journal.id]=name
        returnlist(result_dict.items())


classAccountMoveLine(models.Model):
    _inherit="account.move.line"

    definit(self):
        tools.create_index(self._cr,'account_move_line_move_product_index',self._table,['move_id','product_id'])

    @api.depends('move_id.line_ids','move_id.line_ids.tax_line_id','move_id.line_ids.debit','move_id.line_ids.credit')
    def_compute_tax_base_amount(self):
        aml=self.filtered(lambdal:l.company_id.country_id.code=='IN'andl.tax_line_id andl.product_id)
        formove_lineinaml:
            base_lines=move_line.move_id.line_ids.filtered(lambdaline:move_line.tax_line_idinline.tax_idsandmove_line.product_id==line.product_id)
            move_line.tax_base_amount=abs(sum(base_lines.mapped('balance')))
        remaining_aml=self-aml
        ifremaining_aml:
            returnsuper(AccountMoveLine,remaining_aml)._compute_tax_base_amount()


classAccountTax(models.Model):
    _inherit='account.tax'

    l10n_in_reverse_charge=fields.Boolean("Reversecharge",help="Tickthisifthistaxisreversecharge.OnlyforIndianaccounting")

    defget_grouping_key(self,invoice_tax_val):
        """Returnsastringthatwillbeusedtogroupaccount.invoice.taxsharingthesameproperties"""
        key=super(AccountTax,self).get_grouping_key(invoice_tax_val)
        ifself.company_id.country_id.code=='IN':
            key+="-%s-%s"%(invoice_tax_val.get('l10n_in_product_id',False),
                invoice_tax_val.get('l10n_in_uom_id',False))
        returnkey
