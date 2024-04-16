#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCrmPartnerReportAssign(models.Model):
    """CRMLeadReport"""
    _name="crm.partner.report.assign"
    _auto=False
    _description="CRMPartnershipAnalysis"

    partner_id=fields.Many2one('res.partner','Partner',required=False,readonly=True)
    grade_id=fields.Many2one('res.partner.grade','Grade',readonly=True)
    activation=fields.Many2one('res.partner.activation','Activation',index=True)
    user_id=fields.Many2one('res.users','User',readonly=True)
    date_review=fields.Date('LatestPartnerReview')
    date_partnership=fields.Date('PartnershipDate')
    country_id=fields.Many2one('res.country','Country',readonly=True)
    team_id=fields.Many2one('crm.team','SalesTeam',readonly=True)
    nbr_opportunities=fields.Integer('#ofOpportunity',readonly=True)
    turnover=fields.Float('Turnover',readonly=True)
    date=fields.Date('InvoiceAccountDate',readonly=True)

    _depends={
        'account.invoice.report':['invoice_date','partner_id','price_subtotal','state','move_type'],
        'crm.lead':['partner_assigned_id'],
        'res.partner':['activation','country_id','date_partnership','date_review',
                        'grade_id','parent_id','team_id','user_id'],
    }

    @property
    def_table_query(self):
        """
            CRMLeadReport
            @paramcr:thecurrentrow,fromthedatabasecursor
        """
        return"""
                SELECT
                    COALESCE(2*i.id,2*p.id+1)ASid,
                    p.idaspartner_id,
                    (SELECTcountry_idFROMres_partneraWHEREa.parent_id=p.idANDcountry_idisnotnulllimit1)ascountry_id,
                    p.grade_id,
                    p.activation,
                    p.date_review,
                    p.date_partnership,
                    p.user_id,
                    p.team_id,
                    (SELECTcount(id)FROMcrm_leadWHEREpartner_assigned_id=p.id)ASnbr_opportunities,
                    i.price_subtotalasturnover,
                    i.invoice_dateasdate
                FROM
                    res_partnerp
                    leftjoin({account_invoice_report})i
                        on(i.partner_id=p.idandi.move_typein('out_invoice','out_refund')andi.state='posted')
            """.format(
                account_invoice_report=self.env['account.invoice.report']._table_query
            )
