#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classL10nInExemptedReport(models.Model):
    _name="l10n_in.exempted.report"
    _description="ExemptedGstSuppliedStatistics"
    _auto=False

    account_move_id=fields.Many2one('account.move',string="AccountMove")
    partner_id=fields.Many2one('res.partner',string="Customer")
    out_supply_type=fields.Char(string="OutwardSupplyType")
    in_supply_type=fields.Char(string="InwardSupplyType")
    nil_rated_amount=fields.Float("Nilratedsupplies")
    exempted_amount=fields.Float("Exempted")
    non_gst_supplies=fields.Float("NonGSTSupplies")
    date=fields.Date("Date")
    company_id=fields.Many2one('res.company',string="Company")
    journal_id=fields.Many2one('account.journal',string="Journal")

    def_select(self):
        select_str="""SELECTaml.idASid,
            aml.partner_idASpartner_id,
            am.date,
            aml.balance*(CASEWHENaj.type='sale'THEN-1ELSE1END)ASprice_total,
            am.journal_id,
            aj.company_id,
            aml.move_idasaccount_move_id,

            (CASEWHENp.state_id=cp.state_id
                THEN(CASEWHENp.vatISNOTNULL
                    THEN'Intra-Statesuppliestoregisteredpersons'
                    ELSE'Intra-Statesuppliestounregisteredpersons'
                    END)
                WHENp.state_id!=cp.state_id
                THEN(CASEWHENp.vatISNOTNULL
                    THEN'Inter-Statesuppliestoregisteredpersons'
                    ELSE'Inter-Statesuppliestounregisteredpersons'
                    END)
            END)ASout_supply_type,
            (CASEWHENp.state_id=cp.state_id
                THEN'Intra-Statesupplies'
                WHENp.state_id!=cp.state_id
                THEN'Inter-Statesupplies'
            END)ASin_supply_type,

            (CASEWHEN(
                SELECTMAX(account_tax_id)FROMaccount_move_line_account_tax_rel
                    JOINaccount_taxatONat.id=account_tax_id
                    WHEREaccount_move_line_id=aml.idANDat.tax_group_idIN
                     ((SELECTres_idFROMir_model_dataWHEREmodule='l10n_in'ANDname='nil_rated_group'))
            )ISNOTNULL
                THENaml.balance*(CASEWHENaj.type='sale'THEN-1ELSE1END)
                ELSE0
            END)ASnil_rated_amount,

            (CASEWHEN(
                SELECTMAX(account_tax_id)FROMaccount_move_line_account_tax_rel
                    JOINaccount_taxatONat.id=account_tax_id
                    WHEREaccount_move_line_id=aml.idANDat.tax_group_idIN
                     ((SELECTres_idFROMir_model_dataWHEREmodule='l10n_in'ANDname='exempt_group'))
            )ISNOTNULL
                THENaml.balance*(CASEWHENaj.type='sale'THEN-1ELSE1END)
                ELSE0
            END)ASexempted_amount,

            (CASEWHEN(
                SELECTMAX(account_tax_id)FROMaccount_move_line_account_tax_rel
                    WHEREaccount_move_line_id=aml.id
                )ISNULL
                THENaml.balance*(CASEWHENaj.type='sale'THEN-1ELSE1END)
                ELSE0
            END)ASnon_gst_supplies
        """
        returnselect_str

    def_from(self):
        from_str="""FROMaccount_move_lineaml
            JOINaccount_moveamONam.id=aml.move_id
            JOINaccount_accountaaONaa.id=aml.account_id
            JOINaccount_journalajONaj.id=am.journal_id
            JOINres_companycONc.id=aj.company_id
            LEFTJOINres_partnercpONcp.id=COALESCE(aj.l10n_in_gstin_partner_id,c.partner_id)
            LEFTJOINres_partnerpONp.id=am.partner_id
            LEFTJOINres_countrypcONpc.id=p.country_id
            WHEREaa.internal_type='other'andaml.tax_line_idISNULL
        """
        returnfrom_str

    definit(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self._cr.execute("""CREATEORREPLACEVIEW%sAS(%s%s)"""%(
            self._table,self._select(),self._from()))
