#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classImLivechatReportOperator(models.Model):
    """LivechatSupportReportontheOperator"""

    _name="im_livechat.report.operator"
    _description="LivechatSupportOperatorReport"
    _order='livechat_channel_id,partner_id'
    _auto=False

    partner_id=fields.Many2one('res.partner','Operator',readonly=True)
    livechat_channel_id=fields.Many2one('im_livechat.channel','Channel',readonly=True)
    nbr_channel=fields.Integer('#ofSessions',readonly=True,group_operator="sum",help="Numberofconversation")
    channel_id=fields.Many2one('mail.channel','Conversation',readonly=True)
    start_date=fields.Datetime('StartDateofsession',readonly=True,help="Startdateoftheconversation")
    time_to_answer=fields.Float('Timetoanswer',digits=(16,2),readonly=True,group_operator="avg",help="Averagetimetogivethefirstanswertothevisitor")
    duration=fields.Float('Averageduration',digits=(16,2),readonly=True,group_operator="avg",help="Durationoftheconversation(inseconds)")

    definit(self):
        #Note:start_date_hourmustberemovewhentheread_groupwillallowgroupingonthehourofadatetime.Don'tforgettochangetheview!
        tools.drop_view_if_exists(self.env.cr,'im_livechat_report_operator')
        self.env.cr.execute("""
            CREATEORREPLACEVIEWim_livechat_report_operatorAS(
                SELECT
                    row_number()OVER()ASid,
                    C.livechat_operator_idASpartner_id,
                    C.livechat_channel_idASlivechat_channel_id,
                    COUNT(DISTINCTC.id)ASnbr_channel,
                    C.idASchannel_id,
                    C.create_dateASstart_date,
                    EXTRACT('epoch'FROMMAX(M.create_date)-MIN(M.create_date))ASduration,
                    EXTRACT('epoch'FROMMIN(MO.create_date)-MIN(M.create_date))AStime_to_answer
                FROMmail_channelC
                    JOINmail_message_mail_channel_relRONR.mail_channel_id=C.id
                    JOINmail_messageMONR.mail_message_id=M.id
                    LEFTJOINmail_messageMOON(R.mail_message_id=MO.idANDMO.author_id=C.livechat_operator_id)
                WHEREC.livechat_channel_idISNOTNULL
                GROUPBYC.id,C.livechat_operator_id
            )
        """)
