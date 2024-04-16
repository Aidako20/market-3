#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,tools


classMailingTraceReport(models.Model):
    _name='mailing.trace.report'
    _auto=False
    _description='MassMailingStatistics'

    #mailing
    name=fields.Char(string='MassMail',readonly=True)
    mailing_type=fields.Selection([('mail','Mail')],string='Type',default='mail',required=True)
    campaign=fields.Char(string='MailingCampaign',readonly=True)
    scheduled_date=fields.Datetime(string='ScheduledDate',readonly=True)
    state=fields.Selection(
        [('draft','Draft'),('test','Tested'),('done','Sent')],
        string='Status',readonly=True)
    email_from=fields.Char('From',readonly=True)
    #traces
    sent=fields.Integer(readonly=True)
    delivered=fields.Integer(readonly=True)
    opened=fields.Integer(readonly=True)
    replied=fields.Integer(readonly=True)
    clicked=fields.Integer(readonly=True)
    bounced=fields.Integer(readonly=True)

    definit(self):
        """MassMailStatisticalReport:basedonmailing.tracethatmodelsthevarious
        statisticscollectedforeachmailing,andmailing.mailingmodelthatmodelsthe
        variousmailingperformed."""
        tools.drop_view_if_exists(self.env.cr,'mailing_trace_report')
        self.env.cr.execute(self._report_get_request())

    def_report_get_request(self):
        sql_select='SELECT%s'%','.join(self._report_get_request_select_items())
        sql_from='FROM%s'%''.join(self._report_get_request_from_items())
        sql_where_items=self._report_get_request_where_items()
        ifsql_where_itemsandlen(sql_where_items)==1:
            sql_where='WHERE%s'%sql_where_items[0]
        elifsql_where_items:
            sql_where='WHERE%s'%'AND'.join(sql_where_items)
        else:
            sql_where=''
        sql_group_by='GROUPBY%s'%','.join(self._report_get_request_group_by_items())
        returnf"CREATEORREPLACEVIEWmailing_trace_reportAS({sql_select}{sql_from}{sql_where}{sql_group_by})"

    def_report_get_request_select_items(self):
        return[
            'min(trace.id)asid',
            'utm_source.nameasname',
            'mailing.mailing_type',
            'utm_campaign.nameascampaign',
            'trace.scheduledasscheduled_date',
            'mailing.state',
            'mailing.email_from',
            'count(trace.sent)assent',
            '(count(trace.sent)-count(trace.bounced))asdelivered',
            'count(trace.opened)asopened',
            'count(trace.replied)asreplied',
            'count(trace.clicked)asclicked',
            'count(trace.bounced)asbounced'
        ]

    def_report_get_request_from_items(self):
        return[
            'mailing_traceastrace',
            'leftjoinmailing_mailingasmailingON(trace.mass_mailing_id=mailing.id)',
            'leftjoinutm_campaignasutm_campaignON(mailing.campaign_id=utm_campaign.id)',
            'leftjoinutm_sourceasutm_sourceON(mailing.source_id=utm_source.id)'
        ]

    def_report_get_request_where_items(self):
        return[]

    def_report_get_request_group_by_items(self):
        return[
            'trace.scheduled',
            'utm_source.name',
            'utm_campaign.name',
            'mailing.mailing_type',
            'mailing.state',
            'mailing.email_from'
        ]
