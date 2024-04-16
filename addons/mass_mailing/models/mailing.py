#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib
importhmac
importlogging
importlxml
importrandom
importre
importthreading
importwerkzeug.urls
fromastimportliteral_eval
fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta
fromwerkzeug.urlsimporturl_join

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)

MASS_MAILING_BUSINESS_MODELS=[
    'crm.lead',
    'event.registration',
    'hr.applicant',
    'res.partner',
    'event.track',
    'sale.order',
    'mailing.list',
    'mailing.contact'
]

#SyntaxofthedataURLScheme:https://tools.ietf.org/html/rfc2397#section-3
#Usedtofindinlineimages
image_re=re.compile(r"data:(image/[A-Za-z]+);base64,(.*)")


classMassMailing(models.Model):
    """MassMailingmodelsthesendingofemailstoalistofrecipientsforamassmailingcampaign."""
    _name='mailing.mailing'
    _description='MassMailing'
    _inherit=['mail.thread','mail.activity.mixin','mail.render.mixin']
    _order='sent_dateDESC'
    _inherits={'utm.source':'source_id'}
    _rec_name="subject"

    @api.model
    defdefault_get(self,fields):
        vals=super(MassMailing,self).default_get(fields)
        if'contact_list_ids'infieldsandnotvals.get('contact_list_ids')andvals.get('mailing_model_id'):
            ifvals.get('mailing_model_id')==self.env['ir.model']._get('mailing.list').id:
                mailing_list=self.env['mailing.list'].search([],limit=2)
                iflen(mailing_list)==1:
                    vals['contact_list_ids']=[(6,0,[mailing_list.id])]
        returnvals

    @api.model
    def_get_default_mail_server_id(self):
        server_id=self.env['ir.config_parameter'].sudo().get_param('mass_mailing.mail_server_id')
        try:
            server_id=literal_eval(server_id)ifserver_idelseFalse
            returnself.env['ir.mail_server'].search([('id','=',server_id)]).id
        exceptValueError:
            returnFalse

    active=fields.Boolean(default=True,tracking=True)
    subject=fields.Char('Subject',help='SubjectofyourMailing',required=True,translate=True)
    preview=fields.Char(
        'Preview',translate=True,
        help='Catchypreviewsentencethatencouragesrecipientstoopenthisemail.\n'
             'Inmostinboxes,thisisdisplayednexttothesubject.\n'
             'Keepitemptyifyoupreferthefirstcharactersofyouremailcontenttoappearinstead.')
    email_from=fields.Char(string='SendFrom',required=True,
        default=lambdaself:self.env.user.email_formatted)
    sent_date=fields.Datetime(string='SentDate',copy=False)
    schedule_date=fields.Datetime(string='Scheduledfor',tracking=True)
    #don'ttranslate'body_arch',thetranslationsareonlyon'body_html'
    body_arch=fields.Html(string='Body',translate=False)
    body_html=fields.Html(string='Bodyconvertedtobesentbymail',sanitize_attributes=False)
    attachment_ids=fields.Many2many('ir.attachment','mass_mailing_ir_attachments_rel',
        'mass_mailing_id','attachment_id',string='Attachments')
    keep_archives=fields.Boolean(string='KeepArchives')
    campaign_id=fields.Many2one('utm.campaign',string='UTMCampaign',index=True)
    source_id=fields.Many2one('utm.source',string='Source',required=True,ondelete='cascade',
                                help="Thisisthelinksource,e.g.SearchEngine,anotherdomain,ornameofemaillist")
    medium_id=fields.Many2one(
        'utm.medium',string='Medium',
        compute='_compute_medium_id',readonly=False,store=True,
        help="UTMMedium:deliverymethod(email,sms,...)")
    state=fields.Selection([('draft','Draft'),('in_queue','InQueue'),('sending','Sending'),('done','Sent')],
        string='Status',required=True,tracking=True,copy=False,default='draft',group_expand='_group_expand_states')
    color=fields.Integer(string='ColorIndex')
    user_id=fields.Many2one('res.users',string='Responsible',tracking=True, default=lambdaself:self.env.user)
    #mailingoptions
    mailing_type=fields.Selection([('mail','Email')],string="MailingType",default="mail",required=True)
    reply_to_mode=fields.Selection([
        ('thread','RecipientFollowers'),('email','SpecifiedEmailAddress')],
        string='Reply-ToMode',compute='_compute_reply_to_mode',
        readonly=False,store=True,
        help='Thread:repliesgototargetdocument.Email:repliesareroutedtoagivenemail.')
    reply_to=fields.Char(
        string='ReplyTo',compute='_compute_reply_to',readonly=False,store=True,
        help='PreferredReply-ToAddress')
    #recipients
    mailing_model_real=fields.Char(string='RecipientsRealModel',compute='_compute_model')
    mailing_model_id=fields.Many2one(
        'ir.model',string='RecipientsModel',ondelete='cascade',required=True,
        domain=[('model','in',MASS_MAILING_BUSINESS_MODELS)],
        default=lambdaself:self.env.ref('mass_mailing.model_mailing_list').id)
    mailing_model_name=fields.Char(
        string='RecipientsModelName',related='mailing_model_id.model',
        readonly=True,related_sudo=True)
    mailing_domain=fields.Char(
        string='Domain',compute='_compute_mailing_domain',
        readonly=False,store=True)
    mail_server_id=fields.Many2one('ir.mail_server',string='MailServer',
        default=_get_default_mail_server_id,
        help="Useaspecificmailserverinpriority.OtherwiseFlectrareliesonthefirstoutgoingmailserveravailable(basedontheirsequencing)asitdoesfornormalmails.")
    contact_list_ids=fields.Many2many('mailing.list','mail_mass_mailing_list_rel',string='MailingLists')
    contact_ab_pc=fields.Integer(string='A/BTestingpercentage',
        help='Percentageofthecontactsthatwillbemailed.Recipientswillbetakenrandomly.',default=100)
    unique_ab_testing=fields.Boolean(string='AllowA/BTesting',default=False,
        help='Ifchecked,recipientswillbemailedonlyonceforthewholecampaign.'
             'Thisletsyousenddifferentmailingstorandomlyselectedrecipientsandtest'
             'theeffectivenessofthemailings,withoutcausingduplicatemessages.')
    kpi_mail_required=fields.Boolean('KPImailrequired',copy=False)
    #statisticsdata
    mailing_trace_ids=fields.One2many('mailing.trace','mass_mailing_id',string='EmailsStatistics')
    total=fields.Integer(compute="_compute_total")
    scheduled=fields.Integer(compute="_compute_statistics")
    expected=fields.Integer(compute="_compute_statistics")
    ignored=fields.Integer(compute="_compute_statistics")
    sent=fields.Integer(compute="_compute_statistics")
    delivered=fields.Integer(compute="_compute_statistics")
    opened=fields.Integer(compute="_compute_statistics")
    clicked=fields.Integer(compute="_compute_statistics")
    replied=fields.Integer(compute="_compute_statistics")
    bounced=fields.Integer(compute="_compute_statistics")
    failed=fields.Integer(compute="_compute_statistics")
    received_ratio=fields.Integer(compute="_compute_statistics",string='ReceivedRatio')
    opened_ratio=fields.Integer(compute="_compute_statistics",string='OpenedRatio')
    replied_ratio=fields.Integer(compute="_compute_statistics",string='RepliedRatio')
    bounced_ratio=fields.Integer(compute="_compute_statistics",string='BouncedRatio')
    clicks_ratio=fields.Integer(compute="_compute_clicks_ratio",string="NumberofClicks")
    next_departure=fields.Datetime(compute="_compute_next_departure",string='Scheduleddate')

    def_compute_total(self):
        formass_mailinginself:
            total=self.env[mass_mailing.mailing_model_real].search_count(mass_mailing._parse_mailing_domain())
            ifmass_mailing.contact_ab_pc<100:
                total=int(total/100.0*mass_mailing.contact_ab_pc)
            mass_mailing.total=total

    def_compute_clicks_ratio(self):
        self.env.cr.execute("""
            SELECTCOUNT(DISTINCT(stats.id))ASnb_mails,COUNT(DISTINCT(clicks.mailing_trace_id))ASnb_clicks,stats.mass_mailing_idASid
            FROMmailing_traceASstats
            LEFTOUTERJOINlink_tracker_clickASclicksONclicks.mailing_trace_id=stats.id
            WHEREstats.mass_mailing_idIN%s
            GROUPBYstats.mass_mailing_id
        """,[tuple(self.ids)or(None,)])
        mass_mailing_data=self.env.cr.dictfetchall()
        mapped_data=dict([(m['id'],100*m['nb_clicks']/m['nb_mails'])forminmass_mailing_data])
        formass_mailinginself:
            mass_mailing.clicks_ratio=mapped_data.get(mass_mailing.id,0)

    def_compute_statistics(self):
        """Computestatisticsofthemassmailing"""
        forkeyin(
            'scheduled','expected','ignored','sent','delivered','opened',
            'clicked','replied','bounced','failed','received_ratio',
            'opened_ratio','replied_ratio','bounced_ratio',
        ):
            self[key]=False
        ifnotself.ids:
            return
        #ensuretracesaresenttodb
        self.flush()
        self.env.cr.execute("""
            SELECT
                m.idasmailing_id,
                COUNT(s.id)ASexpected,
                COUNT(CASEWHENs.sentisnotnullTHEN1ELSEnullEND)ASsent,
                COUNT(CASEWHENs.scheduledisnotnullANDs.sentisnullANDs.exceptionisnullANDs.ignoredisnullANDs.bouncedisnullTHEN1ELSEnullEND)ASscheduled,
                COUNT(CASEWHENs.scheduledisnotnullANDs.sentisnullANDs.exceptionisnullANDs.ignoredisnotnullTHEN1ELSEnullEND)ASignored,
                COUNT(CASEWHENs.sentisnotnullANDs.exceptionisnullANDs.bouncedisnullTHEN1ELSEnullEND)ASdelivered,
                COUNT(CASEWHENs.openedisnotnullTHEN1ELSEnullEND)ASopened,
                COUNT(CASEWHENs.clickedisnotnullTHEN1ELSEnullEND)ASclicked,
                COUNT(CASEWHENs.repliedisnotnullTHEN1ELSEnullEND)ASreplied,
                COUNT(CASEWHENs.bouncedisnotnullTHEN1ELSEnullEND)ASbounced,
                COUNT(CASEWHENs.exceptionisnotnullTHEN1ELSEnullEND)ASfailed
            FROM
                mailing_traces
            RIGHTJOIN
                mailing_mailingm
                ON(m.id=s.mass_mailing_id)
            WHERE
                m.idIN%s
            GROUPBY
                m.id
        """,(tuple(self.ids),))
        forrowinself.env.cr.dictfetchall():
            total=(row['expected']-row['ignored'])or1
            row['received_ratio']=100.0*row['delivered']/total
            row['opened_ratio']=100.0*row['opened']/total
            row['replied_ratio']=100.0*row['replied']/total
            row['bounced_ratio']=100.0*row['bounced']/total
            self.browse(row.pop('mailing_id')).update(row)

    def_compute_next_departure(self):
        cron_next_call=self.env.ref('mass_mailing.ir_cron_mass_mailing_queue').sudo().nextcall
        str2dt=fields.Datetime.from_string
        cron_time=str2dt(cron_next_call)
        formass_mailinginself:
            ifmass_mailing.schedule_date:
                schedule_date=str2dt(mass_mailing.schedule_date)
                mass_mailing.next_departure=max(schedule_date,cron_time)
            else:
                mass_mailing.next_departure=cron_time

    @api.depends('mailing_type')
    def_compute_medium_id(self):
        formailinginself:
            ifmailing.mailing_type=='mail'andnotmailing.medium_id:
                mailing.medium_id=self.env.ref('utm.utm_medium_email').id

    @api.depends('mailing_model_id')
    def_compute_model(self):
        forrecordinself:
            record.mailing_model_real=(record.mailing_model_id.model!='mailing.list')andrecord.mailing_model_id.modelor'mailing.contact'

    @api.depends('mailing_model_id')
    def_compute_reply_to_mode(self):
        """Formainmodelsnotreallyusingchattertogatheranswers(contacts
        andmailingcontacts),setreply-toasemail-based.Otherwiseanswers
        bydefaultgoontheoriginaldiscussionthread(businessdocument).Note
        thatmailing_modelbeingmailing.listmeanscontactingmailing.contact
        (seemailing_model_nameversusmailing_model_real)."""
        formailinginself:
            ifmailing.mailing_model_id.modelin['res.partner','mailing.list','mailing.contact']:
                mailing.reply_to_mode='email'
            else:
                mailing.reply_to_mode='thread'

    @api.depends('reply_to_mode')
    def_compute_reply_to(self):
        formailinginself:
            ifmailing.reply_to_mode=='email'andnotmailing.reply_to:
                mailing.reply_to=self.env.user.email_formatted
            elifmailing.reply_to_mode=='thread':
                mailing.reply_to=False

    @api.depends('mailing_model_id','contact_list_ids','mailing_type')
    def_compute_mailing_domain(self):
        formailinginself:
            ifnotmailing.mailing_model_id:
                mailing.mailing_domain=''
            else:
                mailing.mailing_domain=repr(mailing._get_default_mailing_domain())

    #------------------------------------------------------
    #ORM
    #------------------------------------------------------

    @api.model
    defcreate(self,values):
        ifvalues.get('subject')andnotvalues.get('name'):
            values['name']="%s%s"%(values['subject'],datetime.strftime(fields.datetime.now(),tools.DEFAULT_SERVER_DATETIME_FORMAT))
        ifvalues.get('body_html'):
            values['body_html']=self._convert_inline_images_to_urls(values['body_html'])
        returnsuper().create(values)\
            ._fix_attachment_ownership()

    defwrite(self,values):
        ifvalues.get('body_html'):
            values['body_html']=self._convert_inline_images_to_urls(values['body_html'])
        super().write(values)
        self._fix_attachment_ownership()
        returnTrue

    def_fix_attachment_ownership(self):
        forrecordinself:
            record.attachment_ids.write({'res_model':record._name,'res_id':record.id})
        returnself

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        self.ensure_one()
        default=dict(defaultor{},
                       name=_('%s(copy)',self.name),
                       contact_list_ids=self.contact_list_ids.ids)
        returnsuper(MassMailing,self).copy(default=default)

    def_group_expand_states(self,states,domain,order):
        return[keyforkey,valinself._fields['state'].selection]

    #------------------------------------------------------
    #ACTIONS
    #------------------------------------------------------

    defaction_duplicate(self):
        self.ensure_one()
        mass_mailing_copy=self.copy()
        ifmass_mailing_copy:
            context=dict(self.env.context)
            context['form_view_initial_mode']='edit'
            return{
                'type':'ir.actions.act_window',
                'view_mode':'form',
                'res_model':'mailing.mailing',
                'res_id':mass_mailing_copy.id,
                'context':context,
            }
        returnFalse

    defaction_test(self):
        self.ensure_one()
        ctx=dict(self.env.context,default_mass_mailing_id=self.id)
        return{
            'name':_('TestMailing'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mailing.mailing.test',
            'target':'new',
            'context':ctx,
        }

    defaction_schedule(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("mass_mailing.mailing_mailing_schedule_date_action")
        action['context']=dict(self.env.context,default_mass_mailing_id=self.id)
        returnaction

    defaction_put_in_queue(self):
        self.write({'state':'in_queue'})

    defaction_cancel(self):
        self.write({'state':'draft','schedule_date':False,'next_departure':False})

    defaction_retry_failed(self):
        failed_mails=self.env['mail.mail'].sudo().search([
            ('mailing_id','in',self.ids),
            ('state','=','exception')
        ])
        failed_mails.mapped('mailing_trace_ids').unlink()
        failed_mails.unlink()
        self.write({'state':'in_queue'})

    defaction_view_traces_scheduled(self):
        returnself._action_view_traces_filtered('scheduled')

    defaction_view_traces_ignored(self):
        returnself._action_view_traces_filtered('ignored')

    defaction_view_traces_failed(self):
        returnself._action_view_traces_filtered('failed')

    defaction_view_traces_sent(self):
        returnself._action_view_traces_filtered('sent')

    def_action_view_traces_filtered(self,view_filter):
        action=self.env["ir.actions.actions"]._for_xml_id("mass_mailing.mailing_trace_action")
        action['name']=_('%sTraces')%(self.name)
        action['context']={'search_default_mass_mailing_id':self.id,}
        filter_key='search_default_filter_%s'%(view_filter)
        action['context'][filter_key]=True
        returnaction

    defaction_view_clicked(self):
        model_name=self.env['ir.model']._get('link.tracker').display_name
        return{
            'name':model_name,
            'type':'ir.actions.act_window',
            'view_mode':'tree',
            'res_model':'link.tracker',
            'domain':[('mass_mailing_id.id','=',self.id)],
            'context':dict(self._context,create=False)
        }

    defaction_view_opened(self):
        returnself._action_view_documents_filtered('opened')

    defaction_view_replied(self):
        returnself._action_view_documents_filtered('replied')

    defaction_view_bounced(self):
        returnself._action_view_documents_filtered('bounced')

    defaction_view_delivered(self):
        returnself._action_view_documents_filtered('delivered')

    def_action_view_documents_filtered(self,view_filter):
        ifview_filterin('opened','replied','bounced'):
            opened_stats=self.mailing_trace_ids.filtered(lambdastat:stat[view_filter])
        elifview_filter==('delivered'):
            opened_stats=self.mailing_trace_ids.filtered(lambdastat:stat.sentandnotstat.bounced)
        else:
            opened_stats=self.env['mailing.trace']
        res_ids=opened_stats.mapped('res_id')
        model_name=self.env['ir.model']._get(self.mailing_model_real).display_name
        return{
            'name':model_name,
            'type':'ir.actions.act_window',
            'view_mode':'tree',
            'res_model':self.mailing_model_real,
            'domain':[('id','in',res_ids)],
            'context':dict(self._context,create=False)
        }

    defupdate_opt_out(self,email,list_ids,value):
        iflen(list_ids)>0:
            model=self.env['mailing.contact'].with_context(active_test=False)
            records=model.search([('email_normalized','=',tools.email_normalize(email))])
            opt_out_records=self.env['mailing.contact.subscription'].search([
                ('contact_id','in',records.ids),
                ('list_id','in',list_ids),
                ('opt_out','!=',value)
            ])

            opt_out_records.write({'opt_out':value})
            message=_('Therecipient<strong>unsubscribedfrom%s</strong>mailinglist(s)')\
                ifvalueelse_('Therecipient<strong>subscribedto%s</strong>mailinglist(s)')
            forrecordinrecords:
                #filterthelist_idbyrecord
                record_lists=opt_out_records.filtered(lambdarec:rec.contact_id.id==record.id)
                iflen(record_lists)>0:
                    record.sudo().message_post(body=message%','.join(str(list.name)forlistinrecord_lists.mapped('list_id')))

    #------------------------------------------------------
    #EmailSending
    #------------------------------------------------------

    def_get_opt_out_list(self):
        """Returnsasetofemailsopted-outintargetmodel"""
        self.ensure_one()
        opt_out={}
        target=self.env[self.mailing_model_real]
        ifself.mailing_model_real=="mailing.contact":
            #ifuserisopt_outonOnelistbutnotonanother
            #oriftwouserwithsameemailaddress,oneoptedinandtheotheroneoptedout,sendthemailanyway
            #TODODBEFixme:Optimisethefollowingtogetrealopt_outandopt_in
            target_list_contacts=self.env['mailing.contact.subscription'].search(
                [('list_id','in',self.contact_list_ids.ids)])
            opt_out_contacts=target_list_contacts.filtered(lambdarel:rel.opt_out).mapped('contact_id.email_normalized')
            opt_in_contacts=target_list_contacts.filtered(lambdarel:notrel.opt_out).mapped('contact_id.email_normalized')
            opt_out=set(cforcinopt_out_contactsifcnotinopt_in_contacts)

            _logger.info(
                "Mass-mailing%stargets%s,blacklist:%semails",
                self,target._name,len(opt_out))
        else:
            _logger.info("Mass-mailing%stargets%s,nooptoutlistavailable",self,target._name)
        returnopt_out

    def_get_link_tracker_values(self):
        self.ensure_one()
        vals={'mass_mailing_id':self.id}

        ifself.campaign_id:
            vals['campaign_id']=self.campaign_id.id
        ifself.source_id:
            vals['source_id']=self.source_id.id
        ifself.medium_id:
            vals['medium_id']=self.medium_id.id
        returnvals

    def_get_seen_list(self):
        """Returnsasetofemailsalreadytargetedbycurrentmailing/campaign(noduplicates)"""
        self.ensure_one()
        target=self.env[self.mailing_model_real]

        query="""
            SELECTs.email
              FROMmailing_traces
              JOIN%(target)stON(s.res_id=t.id)
             WHEREs.emailISNOTNULL
        """

        ifself.unique_ab_testing:
            query+="""
               ANDs.campaign_id=%%(mailing_campaign_id)s;
            """
        else:
            query+="""
               ANDs.mass_mailing_id=%%(mailing_id)s
               ANDs.model=%%(target_model)s;
            """
        query=query%{'target':target._table}
        params={'mailing_campaign_id':self.campaign_id.id,'mailing_id':self.id,'target_model':self.mailing_model_real}
        self._cr.execute(query,params)
        seen_list=set(m[0]forminself._cr.fetchall())
        _logger.info(
            "Mass-mailing%shasalreadyreached%s%semails",self,len(seen_list),target._name)
        returnseen_list

    def_get_mass_mailing_context(self):
        """Returnsextracontextitemswithpre-filledblacklistandseenlistformassmailing"""
        return{
            'mass_mailing_opt_out_list':self._get_opt_out_list(),
            'mass_mailing_seen_list':self._get_seen_list(),
            'post_convert_links':self._get_link_tracker_values(),
        }

    def_get_recipients(self):
        mailing_domain=self._parse_mailing_domain()
        res_ids=self.env[self.mailing_model_real].search(mailing_domain).ids

        #randomlychooseafragment
        ifself.contact_ab_pc<100:
            contact_nbr=self.env[self.mailing_model_real].search_count(mailing_domain)
            topick=int(contact_nbr/100.0*self.contact_ab_pc)
            ifself.campaign_idandself.unique_ab_testing:
                already_mailed=self.campaign_id._get_mailing_recipients()[self.campaign_id.id]
            else:
                already_mailed=set([])
            remaining=set(res_ids).difference(already_mailed)
            iftopick>len(remaining):
                topick=len(remaining)
            res_ids=random.sample(remaining,topick)
        returnres_ids

    def_get_remaining_recipients(self):
        res_ids=self._get_recipients()
        already_mailed=self.env['mailing.trace'].search_read([
            ('model','=',self.mailing_model_real),
            ('res_id','in',res_ids),
            ('mass_mailing_id','=',self.id)],['res_id'])
        done_res_ids={record['res_id']forrecordinalready_mailed}
        return[ridforridinres_idsifridnotindone_res_ids]

    def_get_unsubscribe_url(self,email_to,res_id):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url=werkzeug.urls.url_join(
            base_url,'mail/mailing/%(mailing_id)s/unsubscribe?%(params)s'%{
                'mailing_id':self.id,
                'params':werkzeug.urls.url_encode({
                    'res_id':res_id,
                    'email':email_to,
                    'token':self._unsubscribe_token(res_id,email_to),
                }),
            }
        )
        returnurl

    def_get_view_url(self,email_to,res_id):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url=werkzeug.urls.url_join(
            base_url,'mailing/%(mailing_id)s/view?%(params)s'%{
                'mailing_id':self.id,
                'params':werkzeug.urls.url_encode({
                    'res_id':res_id,
                    'email':email_to,
                    'token':self._unsubscribe_token(res_id,email_to),
                }),
            }
        )
        returnurl

    defaction_send_mail(self,res_ids=None):
        author_id=self.env.user.partner_id.id

        #Ifnorecipientispassed,wedon'twanttousetherecipientsofthefirst
        #mailingforalltheothers
        initial_res_ids=res_ids
        formailinginself:
            ifnotinitial_res_ids:
                res_ids=mailing._get_remaining_recipients()
            ifnotres_ids:
                raiseUserError(_('Therearenorecipientsselected.'))

            composer_values={
                'author_id':author_id,
                'attachment_ids':[(4,attachment.id)forattachmentinmailing.attachment_ids],
                'body':mailing._prepend_preview(mailing.body_html,mailing.preview),
                'subject':mailing.subject,
                'model':mailing.mailing_model_real,
                'email_from':mailing.email_from,
                'record_name':False,
                'composition_mode':'mass_mail',
                'mass_mailing_id':mailing.id,
                'mailing_list_ids':[(4,l.id)forlinmailing.contact_list_ids],
                'no_auto_thread':mailing.reply_to_mode!='thread',
                'template_id':None,
                'mail_server_id':mailing.mail_server_id.id,
            }
            ifmailing.reply_to_mode=='email':
                composer_values['reply_to']=mailing.reply_to

            composer=self.env['mail.compose.message'].with_context(active_ids=res_ids).create(composer_values)
            extra_context=mailing._get_mass_mailing_context()
            composer=composer.with_context(active_ids=res_ids,**extra_context)
            #auto-commitexceptintestingmode
            auto_commit=notgetattr(threading.currentThread(),'testing',False)
            composer.send_mail(auto_commit=auto_commit)
            mailing.write({
                'state':'done',
                'sent_date':fields.Datetime.now(),
                #sendtheKPImailonlyifit'sthefirstsending
                'kpi_mail_required':notmailing.sent_date,
            })
        returnTrue

    defconvert_links(self):
        res={}
        formass_mailinginself:
            html=mass_mailing.body_htmlifmass_mailing.body_htmlelse''

            vals={'mass_mailing_id':mass_mailing.id}

            ifmass_mailing.campaign_id:
                vals['campaign_id']=mass_mailing.campaign_id.id
            ifmass_mailing.source_id:
                vals['source_id']=mass_mailing.source_id.id
            ifmass_mailing.medium_id:
                vals['medium_id']=mass_mailing.medium_id.id

            res[mass_mailing.id]=mass_mailing._shorten_links(html,vals,blacklist=['/unsubscribe_from_list','/view'])

        returnres

    @api.model
    def_process_mass_mailing_queue(self):
        mass_mailings=self.search([('state','in',('in_queue','sending')),'|',('schedule_date','<',fields.Datetime.now()),('schedule_date','=',False)])
        formass_mailinginmass_mailings:
            user=mass_mailing.write_uidorself.env.user
            mass_mailing=mass_mailing.with_context(**user.with_user(user).context_get())
            iflen(mass_mailing._get_remaining_recipients())>0:
                mass_mailing.state='sending'
                mass_mailing.action_send_mail()
            else:
                mass_mailing.write({
                    'state':'done',
                    'sent_date':fields.Datetime.now(),
                    #sendtheKPImailonlyifit'sthefirstsending
                    'kpi_mail_required':notmass_mailing.sent_date,
                })

        mailings=self.env['mailing.mailing'].search([
            ('kpi_mail_required','=',True),
            ('state','=','done'),
            ('sent_date','<=',fields.Datetime.now()-relativedelta(days=1)),
            ('sent_date','>=',fields.Datetime.now()-relativedelta(days=5)),
        ])
        ifmailings:
            mailings._action_send_statistics()

    #------------------------------------------------------
    #STATISTICS
    #------------------------------------------------------
    def_action_send_statistics(self):
        """Sendanemailtotheresponsibleofeachfinishedmailingwiththestatistics."""
        self.kpi_mail_required=False

        formailinginself:
            user=mailing.user_id
            mailing=mailing.with_context(lang=user.langorself._context.get('lang'))

            link_trackers=self.env['link.tracker'].search(
                [('mass_mailing_id','=',mailing.id)]
            ).sorted('count',reverse=True)
            link_trackers_body=self.env['ir.qweb']._render(
                'mass_mailing.mass_mailing_kpi_link_trackers',
                {'object':mailing,'link_trackers':link_trackers},
            )

            rendered_body=self.env['ir.qweb']._render(
                'digest.digest_mail_main',
                {
                    'body':tools.html_sanitize(link_trackers_body),
                    'company':user.company_id,
                    'user':user,
                    'display_mobile_banner':True,
                    **mailing._prepare_statistics_email_values()
                },
            )

            full_mail=self.env['mail.render.mixin']._render_encapsulate(
                'digest.digest_mail_layout',
                rendered_body,
            )

            mail_values={
                'subject':_('24HStatsofmailing"%s"')%mailing.subject,
                'email_from':user.email_formatted,
                'email_to':user.email_formatted,
                'body_html':full_mail,
                'auto_delete':True,
            }
            mail=self.env['mail.mail'].sudo().create(mail_values)
            mail.send(raise_exception=False)

    def_prepare_statistics_email_values(self):
        """Returnsomestatisticsthatwillbedisplayedinthemailingstatisticsemail.

        Eachiteminthereturnedlistwillbedisplayedasatable,withatitleand
        1,2or3columns.
        """
        self.ensure_one()

        random_tip=self.env['digest.tip'].search(
            [('group_id.category_id','=',self.env.ref('base.module_category_marketing_email_marketing').id)]
        )
        ifrandom_tip:
            random_tip=random.choice(random_tip).tip_description

        formatted_date=tools.format_datetime(
            self.env,self.sent_date,self.user_id.tz,'MMMdd,YYYY', self.user_id.lang
        )ifself.sent_dateelseFalse

        web_base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return{
            'title':_('24HStatsofmailing'),
            'sub_title':'"%s"'%self.subject,
            'top_button_label':_('MoreInfo'),
            'top_button_url':url_join(web_base_url,f'/web#id={self.id}&model=mailing.mailing&view_type=form'),
            'kpi_data':[
                {
                    'kpi_fullname':_('Engagementon%iEmailsSent')%self.sent,
                    'kpi_action':None,
                    'kpi_col1':{
                        'value':f'{self.received_ratio}%',
                        'col_subtitle':'%s(%i)'%(_('RECEIVED'),self.delivered),
                    },
                    'kpi_col2':{
                        'value':f'{self.opened_ratio}%',
                        'col_subtitle':'%s(%i)'%(_('OPENED'),self.opened),
                    },
                    'kpi_col3':{
                        'value':f'{self.replied_ratio}%',
                        'col_subtitle':'%s(%i)'%(_('REPLIED'),self.replied),
                    },
                },{
                    'kpi_fullname':_('BusinessBenefitson%iEmailsSent')%self.sent,
                    'kpi_action':None,
                    'kpi_col1':{},
                    'kpi_col2':{},
                    'kpi_col3':{},
                },
            ],
            'tips':[random_tip]ifrandom_tipelseFalse,
            'formatted_date':formatted_date,
        }

    #------------------------------------------------------
    #TOOLS
    #------------------------------------------------------

    def_get_default_mailing_domain(self):
        mailing_domain=[]
        ifself.mailing_model_name=='mailing.list'andself.contact_list_ids:
            mailing_domain=[('list_ids','in',self.contact_list_ids.ids)]

        ifself.mailing_type=='mail'and'is_blacklisted'inself.env[self.mailing_model_name]._fields:
            mailing_domain=expression.AND([[('is_blacklisted','=',False)],mailing_domain])

        returnmailing_domain

    def_parse_mailing_domain(self):
        self.ensure_one()
        try:
            mailing_domain=literal_eval(self.mailing_domain)
        exceptException:
            mailing_domain=[('id','in',[])]
        returnmailing_domain

    def_unsubscribe_token(self,res_id,email):
        """Generateasecurehashforthismailinglistandparameters.

        ThisisappendedtotheunsubscriptionURLandthencheckedat
        unsubscriptiontimetoensurenomaliciousunsubscriptionsare
        performed.

        :paramintres_id:
            IDoftheresourcethatwillbeunsubscribed.

        :paramstremail:
            Emailoftheresourcethatwillbeunsubscribed.
        """
        secret=self.env["ir.config_parameter"].sudo().get_param("database.secret")
        token=(self.env.cr.dbname,self.id,int(res_id),tools.ustr(email))
        returnhmac.new(secret.encode('utf-8'),repr(token).encode('utf-8'),hashlib.sha512).hexdigest()

    def_convert_inline_images_to_urls(self,body_html):
        """
        Findinlinebase64encodedimages,makeanattachementoutof
        themandreplacetheinlineimagewithanurltotheattachement.
        """

        def_image_to_url(b64image:bytes):
            """Storeanimageinanattachementandreturnsanurl"""
            attachment=self.env['ir.attachment'].create({
                'datas':b64image,
                'name':"cropped_image_mailing_{}".format(self.id),
                'type':'binary',})

            attachment.generate_access_token()

            return'/web/image/%s?access_token=%s'%(
                attachment.id,attachment.access_token)

        modified=False
        root=lxml.html.fromstring(body_html)
        fornodeinroot.iter('img'):
            match=image_re.match(node.attrib.get('src',''))
            ifmatch:
                mime=match.group(1) #unsed
                image=match.group(2).encode() #base64imageasbytes

                node.attrib['src']=_image_to_url(image)
                modified=True

        ifmodified:
            returnlxml.html.tostring(root)

        returnbody_html
