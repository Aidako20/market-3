#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,tools,api


classActivityReport(models.Model):
    """CRMLeadAnalysis"""

    _name="crm.activity.report"
    _auto=False
    _description="CRMActivityAnalysis"
    _rec_name='id'

    date=fields.Datetime('CompletionDate',readonly=True)
    lead_create_date=fields.Datetime('CreationDate',readonly=True)
    date_conversion=fields.Datetime('ConversionDate',readonly=True)
    date_deadline=fields.Date('ExpectedClosing',readonly=True)
    date_closed=fields.Datetime('ClosedDate',readonly=True)
    author_id=fields.Many2one('res.partner','AssignedTo',readonly=True)
    user_id=fields.Many2one('res.users','Salesperson',readonly=True)
    team_id=fields.Many2one('crm.team','SalesTeam',readonly=True)
    lead_id=fields.Many2one('crm.lead',"Opportunity",readonly=True)
    body=fields.Html('ActivityDescription',readonly=True)
    subtype_id=fields.Many2one('mail.message.subtype','Subtype',readonly=True)
    mail_activity_type_id=fields.Many2one('mail.activity.type','ActivityType',readonly=True)
    country_id=fields.Many2one('res.country','Country',readonly=True)
    company_id=fields.Many2one('res.company','Company',readonly=True)
    stage_id=fields.Many2one('crm.stage','Stage',readonly=True)
    partner_id=fields.Many2one('res.partner','Customer',readonly=True)
    lead_type=fields.Selection(
        string='Type',
        selection=[('lead','Lead'),('opportunity','Opportunity')],
        help="TypeisusedtoseparateLeadsandOpportunities")
    active=fields.Boolean('Active',readonly=True)

    def_select(self):
        return"""
            SELECT
                m.id,
                l.create_dateASlead_create_date,
                l.date_conversion,
                l.date_deadline,
                l.date_closed,
                m.subtype_id,
                m.mail_activity_type_id,
                m.author_id,
                m.date,
                m.body,
                l.idaslead_id,
                l.user_id,
                l.team_id,
                l.country_id,
                l.company_id,
                l.stage_id,
                l.partner_id,
                l.typeaslead_type,
                l.active
        """

    def_from(self):
        return"""
            FROMmail_messageASm
        """

    def_join(self):
        return"""
            JOINcrm_leadASlONm.res_id=l.id
        """

    def_where(self):
        disccusion_subtype=self.env.ref('mail.mt_comment')
        return"""
            WHERE
                m.model='crm.lead'AND(m.mail_activity_type_idISNOTNULLORm.subtype_id=%s)
        """%(disccusion_subtype.id,)

    definit(self):
        tools.drop_view_if_exists(self._cr,self._table)
        self._cr.execute("""
            CREATEORREPLACEVIEW%sAS(
                %s
                %s
                %s
                %s
            )
        """%(self._table,self._select(),self._from(),self._join(),self._where())
        )
