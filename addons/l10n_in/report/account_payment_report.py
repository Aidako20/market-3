#-*-coding:utf-8-*-
#azPartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classL10nInPaymentReport(models.AbstractModel):
    _name="l10n_in.payment.report"
    _description="Indianaccountingpaymentreport"

    account_move_id=fields.Many2one('account.move',string="AccountMove")
    payment_id=fields.Many2one('account.payment',string='Payment')
    currency_id=fields.Many2one('res.currency',string="Currency")
    amount=fields.Float(string="Amount")
    payment_amount=fields.Float(string="PaymentAmount")
    partner_id=fields.Many2one('res.partner',string="Customer")
    payment_type=fields.Selection([('outbound','SendMoney'),('inbound','ReceiveMoney')],string='PaymentType')
    journal_id=fields.Many2one('account.journal',string="Journal")
    company_id=fields.Many2one(related="journal_id.company_id",string="Company")
    place_of_supply=fields.Char(string="PlaceofSupply")
    supply_type=fields.Char(string="SupplyType")

    l10n_in_tax_id=fields.Many2one('account.tax',string="Tax")
    tax_rate=fields.Float(string="Rate")
    igst_amount=fields.Float(compute="_compute_tax_amount",string="IGSTamount")
    cgst_amount=fields.Float(compute="_compute_tax_amount",string="CGSTamount")
    sgst_amount=fields.Float(compute="_compute_tax_amount",string="SGSTamount")
    cess_amount=fields.Float(compute="_compute_tax_amount",string="CESSamount")
    gross_amount=fields.Float(compute="_compute_tax_amount",string="Grossadvance")

    def_compute_l10n_in_tax(self,taxes,price_unit,currency=None,quantity=1.0,product=None,partner=None):
        """commonmethodtocomputegsttaxamountbaseontaxgroup"""
        res={'igst_amount':0.0,'sgst_amount':0.0,'cgst_amount':0.0,'cess_amount':0.0}
        AccountTaxRepartitionLine=self.env['account.tax.repartition.line']
        tax_report_line_igst=self.env.ref('l10n_in.tax_report_line_igst',False)
        tax_report_line_cgst=self.env.ref('l10n_in.tax_report_line_cgst',False)
        tax_report_line_sgst=self.env.ref('l10n_in.tax_report_line_sgst',False)
        tax_report_line_cess=self.env.ref('l10n_in.tax_report_line_cess',False)
        filter_tax=taxes.filtered(lambdat:t.type_tax_use!='none')
        tax_compute=filter_tax.compute_all(price_unit,currency=currency,quantity=quantity,product=product,partner=partner)
        fortax_dataintax_compute['taxes']:
            tax_report_lines=AccountTaxRepartitionLine.browse(tax_data['tax_repartition_line_id']).mapped('tag_ids.tax_report_line_ids')
            iftax_report_line_sgstintax_report_lines:
                res['sgst_amount']+=tax_data['amount']
            iftax_report_line_cgstintax_report_lines:
                res['cgst_amount']+=tax_data['amount']
            iftax_report_line_igstintax_report_lines:
                res['igst_amount']+=tax_data['amount']
            iftax_report_line_cessintax_report_lines:
                res['cess_amount']+=tax_data['amount']
        res.update(tax_compute)
        returnres

    #TOBEOVERWRITTEN
    @api.depends('currency_id')
    def_compute_tax_amount(self):
        """Calculatetaxamountbaseondefaulttaxsetincompany"""

    def_select(self):
        return"""SELECTaml.idASid,
            aml.move_idasaccount_move_id,
            ap.idASpayment_id,
            ap.payment_type,
            tax.idasl10n_in_tax_id,
            tax.amountAStax_rate,
            am.partner_id,
            am.amount_totalASpayment_amount,
            am.journal_id,
            aml.currency_id,
            (CASEWHENps.l10n_in_tinISNOTNULL
                THENconcat(ps.l10n_in_tin,'-',ps.name)
                WHENp.idISNULLandcps.l10n_in_tinISNOTNULL
                THENconcat(cps.l10n_in_tin,'-',cps.name)
                ELSE''
                END)ASplace_of_supply,
            (CASEWHENps.id=cp.state_idorp.idISNULL
                THEN'IntraState'
                WHENps.id!=cp.state_idandp.idISNOTNULL
                THEN'InterState'
                END)ASsupply_type"""

    def_from(self):
        return"""FROMaccount_move_lineaml
            JOINaccount_moveamONam.id=aml.move_id
            JOINaccount_paymentapONap.id=aml.payment_id
            JOINaccount_accountASacONac.id=aml.account_id
            JOINaccount_journalASajONaj.id=am.journal_id
            JOINres_companyAScONc.id=aj.company_id
            JOINaccount_taxAStaxONtax.id=(
                CASEWHENap.payment_type='inbound'
                    THENc.account_sale_tax_id
                    ELSEc.account_purchase_tax_idEND)
            JOINres_partnerpONp.id=aml.partner_id
            LEFTJOINres_country_statepsONps.id=p.state_id
            LEFTJOINres_partnercpONcp.id=COALESCE(aj.l10n_in_gstin_partner_id,c.partner_id)
            LEFTJOINres_country_statecpsONcps.id=cp.state_id
            """

    def_where(self):
        return"""WHEREaml.payment_idISNOTNULL
            ANDtax.tax_group_idin(SELECTres_idFROMir_model_dataWHEREmodule='l10n_in'ANDnamein('igst_group','gst_group'))
            ANDac.internal_typeIN('receivable','payable')ANDam.state='posted'"""

    definit(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute("""CREATEorREPLACEVIEW%sAS(
            %s%s%s)"""%(self._table,self._select(),self._from(),self._where()))


classAdvancesPaymentReport(models.Model):
    _name="l10n_in.advances.payment.report"
    _inherit='l10n_in.payment.report'
    _description="AdvancesPaymentAnalysis"
    _auto=False

    date=fields.Date(string="PaymentDate")
    reconcile_amount=fields.Float(string="ReconcileamountinPaymentmonth")

    @api.depends('payment_amount','reconcile_amount','currency_id')
    def_compute_tax_amount(self):
        """Calculatetaxamountbaseondefaulttaxsetincompany"""
        account_move_line=self.env['account.move.line']
        forrecordinself:
            base_amount=record.payment_amount-record.reconcile_amount
            taxes_data=self._compute_l10n_in_tax(
                taxes=record.l10n_in_tax_id,
                price_unit=base_amount,
                currency=record.currency_idorNone,
                quantity=1,
                partner=record.partner_idorNone)
            record.igst_amount=taxes_data['igst_amount']
            record.cgst_amount=taxes_data['cgst_amount']
            record.sgst_amount=taxes_data['sgst_amount']
            record.cess_amount=taxes_data['cess_amount']
            record.gross_amount=taxes_data['total_excluded']

    def_select(self):
        select_str=super(AdvancesPaymentReport,self)._select()
        select_str+=""",
            am.dateasdate,
            (SELECTsum(amount)FROMaccount_partial_reconcileASapr
                WHERE(apr.credit_move_id=aml.idORapr.debit_move_id=aml.id)
                AND(to_char(apr.max_date,'MM-YYYY')=to_char(aml.date,'MM-YYYY'))
            )ASreconcile_amount,
            (am.amount_total-(SELECT(CASEWHENSUM(amount)ISNULLTHEN0ELSESUM(amount)END)FROMaccount_partial_reconcileASapr
                WHERE(apr.credit_move_id=aml.idORapr.debit_move_id=aml.id)
                AND(to_char(apr.max_date,'MM-YYYY')=to_char(aml.date,'MM-YYYY'))
            ))ASamount"""
        returnselect_str


classL10nInAdvancesPaymentAdjustmentReport(models.Model):
    _name="l10n_in.advances.payment.adjustment.report"
    _inherit='l10n_in.payment.report'
    _description="AdvancesPaymentAdjustmentAnalysis"
    _auto=False

    date=fields.Date('ReconcileDate')

    @api.depends('amount','currency_id','partner_id')
    def_compute_tax_amount(self):
        account_move_line=self.env['account.move.line']
        forrecordinself:
            taxes_data=self._compute_l10n_in_tax(
                taxes=record.l10n_in_tax_id,
                price_unit=record.amount,
                currency=record.currency_idorNone,
                quantity=1,
                partner=record.partner_idorNone)
            record.igst_amount=taxes_data['igst_amount']
            record.cgst_amount=taxes_data['cgst_amount']
            record.sgst_amount=taxes_data['sgst_amount']
            record.cess_amount=taxes_data['cess_amount']
            record.gross_amount=taxes_data['total_excluded']

    def_select(self):
        select_str=super(L10nInAdvancesPaymentAdjustmentReport,self)._select()
        select_str+=""",
            apr.max_dateASdate,
            apr.amountASamount
            """
        returnselect_str

    def_from(self):
        from_str=super(L10nInAdvancesPaymentAdjustmentReport,self)._from()
        from_str+="""
            JOINaccount_partial_reconcileaprONapr.credit_move_id=aml.idORapr.debit_move_id=aml.id
            """
        returnfrom_str

    def_where(self):
        where_str=super(L10nInAdvancesPaymentAdjustmentReport,self)._where()
        where_str+="""
            AND(apr.max_date>aml.date)
        """
        returnwhere_str
