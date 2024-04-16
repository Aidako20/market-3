#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classAccountAnalyticAccount(models.Model):
    _inherit='account.analytic.account'

    @api.constrains('company_id')
    def_check_company_consistency(self):
        analytic_accounts=self.filtered('company_id')

        ifnotanalytic_accounts:
            return

        self.flush(['company_id'])
        self._cr.execute('''
            SELECTline.id
            FROMaccount_move_lineline
            JOINaccount_analytic_accountaccountONaccount.id=line.analytic_account_id
            WHEREline.analytic_account_idIN%s
            ANDline.company_id!=account.company_id
        ''',[tuple(analytic_accounts.ids)])

        ifself._cr.fetchone():
            raiseUserError(_("Youcan'tsetadifferentcompanyonyouranalyticaccountsincetherearesomejournalitemslinkedtoit."))


classAccountAnalyticTag(models.Model):
    _inherit='account.analytic.tag'

    @api.constrains('company_id')
    def_check_company_consistency(self):
        analytic_tags=self.filtered('company_id')

        ifnotanalytic_tags:
            return

        self.flush(['company_id'])
        self._cr.execute('''
            SELECTline.id
            FROMaccount_analytic_tag_account_move_line_reltag_rel
            JOINaccount_analytic_tagtagONtag.id=tag_rel.account_analytic_tag_id
            JOINaccount_move_linelineONline.id=tag_rel.account_move_line_id
            WHEREtag_rel.account_analytic_tag_idIN%s
            ANDline.company_id!=tag.company_id
        ''',[tuple(analytic_tags.ids)])

        ifself._cr.fetchone():
            raiseUserError(_("Youcan'tsetadifferentcompanyonyouranalytictagssincetherearesomejournalitemslinkedtoit."))


classAccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'
    _description='AnalyticLine'

    product_id=fields.Many2one('product.product',string='Product',check_company=True)
    general_account_id=fields.Many2one('account.account',string='FinancialAccount',ondelete='restrict',readonly=True,
                                         related='move_id.account_id',store=True,domain="[('deprecated','=',False),('company_id','=',company_id)]",
                                         compute_sudo=True)
    move_id=fields.Many2one('account.move.line',string='JournalItem',ondelete='cascade',index=True,check_company=True)
    code=fields.Char(size=8)
    ref=fields.Char(string='Ref.')

    @api.onchange('product_id','product_uom_id','unit_amount','currency_id')
    defon_change_unit_amount(self):
        ifnotself.product_id:
            return{}

        result=0.0
        prod_accounts=self.product_id.product_tmpl_id.with_company(self.company_id)._get_product_accounts()
        unit=self.product_uom_id
        account=prod_accounts['expense']
        ifnotunitorself.product_id.uom_po_id.category_id.id!=unit.category_id.id:
            unit=self.product_id.uom_po_id

        #Computebasedonpricetype
        amount_unit=self.product_id.price_compute('standard_price',uom=unit)[self.product_id.id]
        amount=amount_unit*self.unit_amountor0.0
        result=(self.currency_id.round(amount)ifself.currency_idelseround(amount,2))*-1
        self.amount=result
        self.general_account_id=account
        self.product_uom_id=unit

    @api.model
    defview_header_get(self,view_id,view_type):
        ifself.env.context.get('account_id'):
            return_(
                "Entries:%(account)s",
                account=self.env['account.analytic.account'].browse(self.env.context['account_id']).name
            )
        returnsuper().view_header_get(view_id,view_type)
