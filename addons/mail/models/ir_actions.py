#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError,ValidationError


classServerActions(models.Model):
    """Addemailoptioninserveractions."""
    _name='ir.actions.server'
    _description='ServerAction'
    _inherit=['ir.actions.server']

    state=fields.Selection(selection_add=[
        ('email','SendEmail'),
        ('followers','AddFollowers'),
        ('next_activity','CreateNextActivity'),
        ],ondelete={'email':'cascade','followers':'cascade','next_activity':'cascade'})
    #Followers
    partner_ids=fields.Many2many('res.partner',string='AddFollowers')
    channel_ids=fields.Many2many('mail.channel',string='AddChannels')
    #Template
    template_id=fields.Many2one(
        'mail.template','EmailTemplate',ondelete='setnull',
        domain="[('model_id','=',model_id)]",
    )
    #NextActivity
    activity_type_id=fields.Many2one(
        'mail.activity.type',string='Activity',
        domain="['|',('res_model_id','=',False),('res_model_id','=',model_id)]",
        ondelete='restrict')
    activity_summary=fields.Char('Summary')
    activity_note=fields.Html('Note')
    activity_date_deadline_range=fields.Integer(string='DueDateIn')
    activity_date_deadline_range_type=fields.Selection([
        ('days','Days'),
        ('weeks','Weeks'),
        ('months','Months'),
    ],string='Duetype',default='days')
    activity_user_type=fields.Selection([
        ('specific','SpecificUser'),
        ('generic','GenericUserFromRecord')],default="specific",required=True,
        help="Use'SpecificUser'toalwaysassignthesameuseronthenextactivity.Use'GenericUserFromRecord'tospecifythefieldnameoftheusertochooseontherecord.")
    activity_user_id=fields.Many2one('res.users',string='Responsible')
    activity_user_field_name=fields.Char('Userfieldname',help="Technicalnameoftheuserontherecord",default="user_id")

    @api.onchange('activity_date_deadline_range')
    def_onchange_activity_date_deadline_range(self):
        ifself.activity_date_deadline_range<0:
            raiseUserError(_("The'DueDateIn'valuecan'tbenegative."))

    @api.constrains('state','model_id')
    def_check_mail_thread(self):
        foractioninself:
            ifaction.state=='followers'andnotaction.model_id.is_mail_thread:
                raiseValidationError(_("AddFollowerscanonlybedoneonamailthreadmodel"))

    @api.constrains('state','model_id')
    def_check_activity_mixin(self):
        foractioninself:
            ifaction.state=='next_activity'andnotaction.model_id.is_mail_thread:
                raiseValidationError(_("Anextactivitycanonlybeplannedonmodelsthatusethechatter"))

    def_run_action_followers_multi(self,eval_context=None):
        Model=self.env[self.model_name]
        ifself.partner_idsorself.channel_idsandhasattr(Model,'message_subscribe'):
            records=Model.browse(self._context.get('active_ids',self._context.get('active_id')))
            records.message_subscribe(self.partner_ids.ids,self.channel_ids.ids)
        returnFalse

    def_is_recompute(self):
        """Whenanactivityissetonupdateofarecord,
        updatemightbetriggeredmanytimesbyrecomputes.
        Whenneedtoknowittoskipthesesteps.
        Exceptifthecomputedfieldissupposedtotriggertheaction
        """
        records=self.env[self.model_name].browse(
            self._context.get('active_ids',self._context.get('active_id')))
        old_values=self._context.get('old_values')
        ifold_values:
            domain_post=self._context.get('domain_post')
            tracked_fields=[]
            ifdomain_post:
                forleafindomain_post:
                    ifisinstance(leaf,(tuple,list)):
                        tracked_fields.append(leaf[0])
            fields_to_check=[fieldforrecord,field_namesinold_values.items()forfieldinfield_namesiffieldnotintracked_fields]
            iffields_to_check:
                field=records._fields[fields_to_check[0]]
                #Pickanarbitraryfield;ifitismarkedtoberecomputed,
                #itmeansweareinanextraneouswritetriggeredbytherecompute.
                #Inthiscase,weshouldnotcreateanewactivity.
                ifrecords&self.env.records_to_compute(field):
                    returnTrue
        returnFalse

    def_run_action_email(self,eval_context=None):
        #TDECLEANME:whengoingtonewapiwithserveraction,removeaction
        ifnotself.template_idornotself._context.get('active_id')orself._is_recompute():
            returnFalse
        #Cleancontextfromdefault_typetoavoidmakingattachment
        #withwrongvaluesinsubsequentoperations
        cleaned_ctx=dict(self.env.context)
        cleaned_ctx.pop('default_type',None)
        cleaned_ctx.pop('default_parent_id',None)
        self.template_id.with_context(cleaned_ctx).send_mail(self._context.get('active_id'),force_send=False,
                                                             raise_exception=False)
        returnFalse

    def_run_action_next_activity(self,eval_context=None):
        ifnotself.activity_type_idornotself._context.get('active_id')orself._is_recompute():
            returnFalse

        records=self.env[self.model_name].browse(self._context.get('active_ids',self._context.get('active_id')))

        vals={
            'summary':self.activity_summaryor'',
            'note':self.activity_noteor'',
            'activity_type_id':self.activity_type_id.id,
        }
        ifself.activity_date_deadline_range>0:
            vals['date_deadline']=fields.Date.context_today(self)+relativedelta(**{
                self.activity_date_deadline_range_type:self.activity_date_deadline_range})
        forrecordinrecords:
            user=False
            ifself.activity_user_type=='specific':
                user=self.activity_user_id
            elifself.activity_user_type=='generic'andself.activity_user_field_nameinrecord:
                user=record[self.activity_user_field_name]
            ifuser:
                vals['user_id']=user.id
            record.activity_schedule(**vals)
        returnFalse

    @api.model
    def_get_eval_context(self,action=None):
        """Overridethemethodgivingtheevaluationcontextbutalsothe
        contextusedinallsubsequentcalls.Addthemail_notify_force_send
        keysettoFalseinthecontext.Thiswayallnotificationemailslinked
        tothecurrentlyexecutedactionwillbesetinthequeueinsteadof
        sentdirectly.Thiswillavoidpossiblebreakintransactions."""
        eval_context=super(ServerActions,self)._get_eval_context(action=action)
        ctx=dict(eval_context['env'].context)
        ctx['mail_notify_force_send']=False
        eval_context['env'].context=ctx
        returneval_context
