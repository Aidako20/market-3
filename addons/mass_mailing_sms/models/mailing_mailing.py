#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)


classMailing(models.Model):
    _inherit='mailing.mailing'

    @api.model
    defdefault_get(self,fields):
        res=super(Mailing,self).default_get(fields)
        iffieldsisnotNoneand'keep_archives'infieldsandres.get('mailing_type')=='sms':
            res['keep_archives']=True
        returnres

    #mailingoptions
    mailing_type=fields.Selection(selection_add=[
        ('sms','SMS')
    ],ondelete={'sms':'setdefault'})

    #'sms_subject'addedtooverride'subject'field(stringattributeshouldbelabelled"Title"whenmailing_type=='sms').
    #'sms_subject'shouldhavethesamehelperas'subject'fieldwhen'mass_mailing_sms'installed.
    #otherwise'sms_subject'willgettheoldhelperfrom'mass_mailing'module.
    #overriding'subject'fieldhelperinthismodelisnotworking,sincethehelperwillkeepthenewvalue
    #evenwhen'mass_mailing_sms'removed(see'mailing_mailing_view_form_sms'formoredetails).                   
    sms_subject=fields.Char('Title',help='Foranemail,thesubjectyourrecipientswillseeintheirinbox.\n'
                              'ForanSMS,theinternaltitleofthemessage.',
                              related='subject',translate=True,readonly=False)
    #smsoptions
    body_plaintext=fields.Text('SMSBody',compute='_compute_body_plaintext',store=True,readonly=False)
    sms_template_id=fields.Many2one('sms.template',string='SMSTemplate',ondelete='setnull')
    sms_has_insufficient_credit=fields.Boolean(
        'InsufficientIAPcredits',compute='_compute_sms_has_iap_failure',
        help='UXFieldtoproposetobuyIAPcredits')
    sms_has_unregistered_account=fields.Boolean(
        'UnregisteredIAPaccount',compute='_compute_sms_has_iap_failure',
        help='UXFieldtoproposetoRegistertheSMSIAPaccount')
    sms_force_send=fields.Boolean(
        'SendDirectly',help='Useatyourownrisks.')
    #opt_out_link
    sms_allow_unsubscribe=fields.Boolean('Includeopt-outlink',default=False)

    @api.depends('mailing_type')
    def_compute_medium_id(self):
        super(Mailing,self)._compute_medium_id()
        formailinginself:
            ifmailing.mailing_type=='sms'and(notmailing.medium_idormailing.medium_id==self.env.ref('utm.utm_medium_email')):
                mailing.medium_id=self.env.ref('mass_mailing_sms.utm_medium_sms').id
            elifmailing.mailing_type=='mail'and(notmailing.medium_idormailing.medium_id==self.env.ref('mass_mailing_sms.utm_medium_sms')):
                mailing.medium_id=self.env.ref('utm.utm_medium_email').id

    @api.depends('sms_template_id','mailing_type')
    def_compute_body_plaintext(self):
        formailinginself:
            ifmailing.mailing_type=='sms'andmailing.sms_template_id:
                mailing.body_plaintext=mailing.sms_template_id.body

    @api.depends('mailing_trace_ids.failure_type')
    def_compute_sms_has_iap_failure(self):
        failures=['sms_acc','sms_credit']
        ifnotself.ids:
            self.sms_has_insufficient_credit=self.sms_has_unregistered_account=False
        else:
            traces=self.env['mailing.trace'].sudo().read_group([
                        ('mass_mailing_id','in',self.ids),
                        ('trace_type','=','sms'),
                        ('failure_type','in',failures)
            ],['mass_mailing_id','failure_type'],['mass_mailing_id','failure_type'],lazy=False)

            trace_dict=dict.fromkeys(self.ids,{key:Falseforkeyinfailures})
            fortintraces:
                trace_dict[t['mass_mailing_id'][0]][t['failure_type']]= t['__count']andTrueorFalse

            formailinself:
                mail.sms_has_insufficient_credit=trace_dict[mail.id]['sms_credit']
                mail.sms_has_unregistered_account=trace_dict[mail.id]['sms_acc']


    #--------------------------------------------------
    #ORMOVERRIDES
    #--------------------------------------------------

    @api.model
    defcreate(self,values):
        #Getsubjectfrom"sms_subject"fieldwhenSMSinstalled(usedtobuildthenameofrecordinthesuper'create'method)
        ifvalues.get('mailing_type')=='sms'andvalues.get('sms_subject'):
            values['subject']=values['sms_subject']
        returnsuper(Mailing,self).create(values)

    #--------------------------------------------------
    #BUSINESS/VIEWSACTIONS
    #--------------------------------------------------

    defaction_put_in_queue_sms(self):
        res=self.action_put_in_queue()
        ifself.sms_force_send:
            self.action_send_mail()
        returnres

    defaction_send_now_sms(self):
        ifnotself.sms_force_send:
            self.write({'sms_force_send':True})
        returnself.action_send_mail()

    defaction_retry_failed(self):
        mass_sms=self.filtered(lambdam:m.mailing_type=='sms')
        ifmass_sms:
            mass_sms.action_retry_failed_sms()
        returnsuper(Mailing,self-mass_sms).action_retry_failed()

    defaction_retry_failed_sms(self):
        failed_sms=self.env['sms.sms'].sudo().search([
            ('mailing_id','in',self.ids),
            ('state','=','error')
        ])
        failed_sms.mapped('mailing_trace_ids').unlink()
        failed_sms.unlink()
        self.write({'state':'in_queue'})

    defaction_test(self):
        ifself.mailing_type=='sms':
            ctx=dict(self.env.context,default_mailing_id=self.id)
            return{
                'name':_('TestSMSmarketing'),
                'type':'ir.actions.act_window',
                'view_mode':'form',
                'res_model':'mailing.sms.test',
                'target':'new',
                'context':ctx,
            }
        returnsuper(Mailing,self).action_test()

    def_action_view_traces_filtered(self,view_filter):
        action=super(Mailing,self)._action_view_traces_filtered(view_filter)
        ifself.mailing_type=='sms':
            action['views']=[(self.env.ref('mass_mailing_sms.mailing_trace_view_tree_sms').id,'tree'),
                               (self.env.ref('mass_mailing_sms.mailing_trace_view_form_sms').id,'form')]
        returnaction

    defaction_buy_sms_credits(self):
        url=self.env['iap.account'].get_credits_url(service_name='sms')
        return{
            'type':'ir.actions.act_url',
            'url':url,
        }

    #--------------------------------------------------
    #SMSSEND
    #--------------------------------------------------

    def_get_opt_out_list_sms(self):
        """Returnsasetofemailsopted-outintargetmodel"""
        self.ensure_one()
        opt_out=[]
        target=self.env[self.mailing_model_real]
        ifself.mailing_model_real=='mailing.contact':
            #ifuserisopt_outonOnelistbutnotonanother
            #oriftwouserwithsameemailaddress,oneoptedinandtheotheroneoptedout,sendthemailanyway
            #TODODBEFixme:Optimisethefollowingtogetrealopt_outandopt_in
            subscriptions=self.env['mailing.contact.subscription'].sudo().search(
                [('list_id','in',self.contact_list_ids.ids)])
            opt_out_contacts=subscriptions.filtered(lambdasub:sub.opt_out).mapped('contact_id')
            opt_in_contacts=subscriptions.filtered(lambdasub:notsub.opt_out).mapped('contact_id')
            opt_out=list(set(c.idforcinopt_out_contactsifcnotinopt_in_contacts))

            _logger.info("MassSMS%stargets%s:optout:%scontacts",self,target._name,len(opt_out))
        else:
            _logger.info("MassSMS%stargets%s:nooptoutlistavailable",self,target._name)
        returnopt_out

    def_get_seen_list_sms(self):
        """Returnsasetofemailsalreadytargetedbycurrentmailing/campaign(noduplicates)"""
        self.ensure_one()
        target=self.env[self.mailing_model_real]

        partner_fields=[]
        ifisinstance(target,self.pool['mail.thread.phone']):
            phone_fields=['phone_sanitized']
        elifisinstance(target,self.pool['mail.thread']):
            phone_fields=[
                fnameforfnameintarget._sms_get_number_fields()
                iffnameintarget._fieldsandtarget._fields[fname].store
            ]
            partner_fields=target._sms_get_partner_fields()
        else:
            phone_fields=[]
            if'mobile'intarget._fieldsandtarget._fields['mobile'].store:
                phone_fields.append('mobile')
            if'phone'intarget._fieldsandtarget._fields['phone'].store:
                phone_fields.append('phone')
        partner_field=next(
            (fnameforfnameinpartner_fieldsiftarget._fields[fname].storeandtarget._fields[fname].type=='many2one'),
            False
        )
        ifnotphone_fieldsandnotpartner_field:
            raiseUserError(_("Unsupported%sformassSMS",self.mailing_model_id.name))

        query="""
            SELECT%(select_query)s
              FROMmailing_tracetrace
              JOIN%(target_table)stargetON(trace.res_id=target.id)
              %(join_add_query)s
             WHERE(%(where_query)s)
               ANDtrace.mass_mailing_id=%%(mailing_id)s
               ANDtrace.model=%%(target_model)s
        """
        ifphone_fields:
            #phonefieldsarecheckedontargetmailedmodel
            select_query='target.id,'+','.join('target.%s'%fnameforfnameinphone_fields)
            where_query='OR'.join('target.%sISNOTNULL'%fnameforfnameinphone_fields)
            join_add_query=''
        else:
            #phonefieldsarecheckedonres.partnermodel
            partner_phone_fields=['mobile','phone']
            select_query='target.id,'+','.join('partner.%s'%fnameforfnameinpartner_phone_fields)
            where_query='OR'.join('partner.%sISNOTNULL'%fnameforfnameinpartner_phone_fields)
            join_add_query='JOINres_partnerpartnerON(target.%s=partner.id)'%partner_field

        query=query%{
            'select_query':select_query,
            'where_query':where_query,
            'target_table':target._table,
            'join_add_query':join_add_query,
        }
        params={'mailing_id':self.id,'target_model':self.mailing_model_real}
        self._cr.execute(query,params)
        query_res=self._cr.fetchall()
        seen_list=set(numberforiteminquery_resfornumberinitem[1:]ifnumber)
        seen_ids=set(item[0]foriteminquery_res)
        _logger.info("MassSMS%stargets%s:alreadyreached%sSMS",self,target._name,len(seen_list))
        returnlist(seen_ids),list(seen_list)

    def_send_sms_get_composer_values(self,res_ids):
        return{
            #content
            'body':self.body_plaintext,
            'template_id':self.sms_template_id.id,
            'res_model':self.mailing_model_real,
            'res_ids':repr(res_ids),
            #options
            'composition_mode':'mass',
            'mailing_id':self.id,
            'mass_keep_log':self.keep_archives,
            'mass_force_send':self.sms_force_send,
            'mass_sms_allow_unsubscribe':self.sms_allow_unsubscribe,
        }

    defaction_send_mail(self,res_ids=None):
        mass_sms=self.filtered(lambdam:m.mailing_type=='sms')
        ifmass_sms:
            mass_sms.action_send_sms(res_ids=res_ids)
        returnsuper(Mailing,self-mass_sms).action_send_mail(res_ids=res_ids)

    defaction_send_sms(self,res_ids=None):
        formailinginself:
            ifnotres_ids:
                res_ids=mailing._get_remaining_recipients()
            ifnotres_ids:
                raiseUserError(_('Therearenorecipientsselected.'))

            composer=self.env['sms.composer'].with_context(active_id=False).create(mailing._send_sms_get_composer_values(res_ids))
            composer._action_send_sms()
            mailing.write({'state':'done','sent_date':fields.Datetime.now()})
        returnTrue

    #--------------------------------------------------
    #TOOLS
    #--------------------------------------------------

    def_get_default_mailing_domain(self):
        mailing_domain=super(Mailing,self)._get_default_mailing_domain()
        ifself.mailing_type=='sms'and'phone_sanitized_blacklisted'inself.env[self.mailing_model_name]._fields:
            mailing_domain=expression.AND([mailing_domain,[('phone_sanitized_blacklisted','=',False)]])

        returnmailing_domain
