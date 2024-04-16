#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromdatetimeimportdate,datetime
fromdateutil.relativedeltaimportrelativedelta
importlogging
importpytz

fromflectraimportapi,exceptions,fields,models,_
fromflectra.osvimportexpression

fromflectra.tools.miscimportclean_context
fromflectra.addons.base.models.ir_modelimportMODULE_UNINSTALL_FLAG

_logger=logging.getLogger(__name__)


classMailActivityType(models.Model):
    """ActivityTypesareusedtocategorizeactivities.Eachtypeisadifferent
    kindofactivitye.g.call,mail,meeting.Anactivitycanbegenerici.e.
    availableforallmodelsusingactivities;orspecifictoamodelinwhich
    caseres_model_idfieldshouldbeused."""
    _name='mail.activity.type'
    _description='ActivityType'
    _rec_name='name'
    _order='sequence,id'

    @api.model
    defdefault_get(self,fields):
        ifnotself.env.context.get('default_res_model_id')andself.env.context.get('default_res_model'):
            self=self.with_context(
                default_res_model_id=self.env['ir.model']._get(self.env.context.get('default_res_model'))
            )
        returnsuper(MailActivityType,self).default_get(fields)

    name=fields.Char('Name',required=True,translate=True)
    summary=fields.Char('DefaultSummary',translate=True)
    sequence=fields.Integer('Sequence',default=10)
    active=fields.Boolean(default=True)
    create_uid=fields.Many2one('res.users',index=True)
    delay_count=fields.Integer(
        'ScheduledDate',default=0,
        help='Numberofdays/week/monthbeforeexecutingtheaction.Itallowstoplantheactiondeadline.')
    delay_unit=fields.Selection([
        ('days','days'),
        ('weeks','weeks'),
        ('months','months')],string="Delayunits",help="Unitofdelay",required=True,default='days')
    delay_label=fields.Char(compute='_compute_delay_label')
    delay_from=fields.Selection([
        ('current_date','aftervalidationdate'),
        ('previous_activity','afterpreviousactivitydeadline')],string="DelayType",help="Typeofdelay",required=True,default='previous_activity')
    icon=fields.Char('Icon',help="Fontawesomeicone.g.fa-tasks")
    decoration_type=fields.Selection([
        ('warning','Alert'),
        ('danger','Error')],string="DecorationType",
        help="Changethebackgroundcoloroftherelatedactivitiesofthistype.")
    res_model_id=fields.Many2one(
        'ir.model','Model',index=True,
        domain=['&',('is_mail_thread','=',True),('transient','=',False)],
        help='Specifyamodeliftheactivityshouldbespecifictoamodel'
             'andnotavailablewhenmanagingactivitiesforothermodels.')
    default_next_type_id=fields.Many2one('mail.activity.type','DefaultNextActivity',
        domain="['|',('res_model_id','=',False),('res_model_id','=',res_model_id)]",ondelete='restrict')
    force_next=fields.Boolean("TriggerNextActivity",default=False)
    next_type_ids=fields.Many2many(
        'mail.activity.type','mail_activity_rel','activity_id','recommended_id',
        domain="['|',('res_model_id','=',False),('res_model_id','=',res_model_id)]",
        string='RecommendedNextActivities')
    previous_type_ids=fields.Many2many(
        'mail.activity.type','mail_activity_rel','recommended_id','activity_id',
        domain="['|',('res_model_id','=',False),('res_model_id','=',res_model_id)]",
        string='PrecedingActivities')
    category=fields.Selection([
        ('default','None'),('upload_file','UploadDocument')
    ],default='default',string='ActiontoPerform',
        help='Actionsmaytriggerspecificbehaviorlikeopeningcalendarvieworautomaticallymarkasdonewhenadocumentisuploaded')
    mail_template_ids=fields.Many2many('mail.template',string='Emailtemplates')
    default_user_id=fields.Many2one("res.users",string="DefaultUser")
    default_description=fields.Html(string="DefaultDescription",translate=True)

    #Fieldsfordisplaypurposeonly
    initial_res_model_id=fields.Many2one('ir.model','Initialmodel',compute="_compute_initial_res_model_id",store=False,
            help='TechnicalfieldtokeeptrackofthemodelatthestartofeditingtosupportUXrelatedbehaviour')
    res_model_change=fields.Boolean(string="Modelhaschange",help="TechnicalfieldforUXrelatedbehaviour",default=False,store=False)

    @api.onchange('res_model_id')
    def_onchange_res_model_id(self):
        self.mail_template_ids=self.mail_template_ids.filtered(lambdatemplate:template.model_id==self.res_model_id)
        self.res_model_change=self.initial_res_model_idandself.initial_res_model_id!=self.res_model_id

    def_compute_initial_res_model_id(self):
        foractivity_typeinself:
            activity_type.initial_res_model_id=activity_type.res_model_id

    @api.depends('delay_unit','delay_count')
    def_compute_delay_label(self):
        selection_description_values={
            e[0]:e[1]foreinself._fields['delay_unit']._description_selection(self.env)}
        foractivity_typeinself:
            unit=selection_description_values[activity_type.delay_unit]
            activity_type.delay_label='%s%s'%(activity_type.delay_count,unit)


classMailActivity(models.Model):
    """Anactualactivitytoperform.Activitiesarelinkedto
    documentsusingres_idandres_model_idfields.Activitieshaveadeadline
    thatcanbeusedinkanbanviewtodisplayastatus.Oncedoneactivities
    areunlinkedandamessageisposted.Thismessagehasanewactivity_type_id
    fieldthatindicatestheactivitylinkedtothemessage."""
    _name='mail.activity'
    _description='Activity'
    _order='date_deadlineASC'
    _rec_name='summary'

    @api.model
    defdefault_get(self,fields):
        res=super(MailActivity,self).default_get(fields)
        ifnotfieldsor'res_model_id'infieldsandres.get('res_model'):
            res['res_model_id']=self.env['ir.model']._get(res['res_model']).id
        returnres

    @api.model
    def_default_activity_type_id(self):
        ActivityType=self.env["mail.activity.type"]
        activity_type_todo=self.env.ref('mail.mail_activity_data_todo',raise_if_not_found=False)
        default_vals=self.default_get(['res_model_id','res_model'])
        ifnotdefault_vals.get('res_model_id'):
            returnActivityType
        current_model_id=default_vals['res_model_id']
        ifactivity_type_todoandactivity_type_todo.activeand(activity_type_todo.res_model_id.id==current_model_idornotactivity_type_todo.res_model_id):
            returnactivity_type_todo
        activity_type_model=ActivityType.search([('res_model_id','=',current_model_id)],limit=1)
        ifactivity_type_model:
            returnactivity_type_model
        activity_type_generic=ActivityType.search([('res_model_id','=',False)],limit=1)
        returnactivity_type_generic

    #owner
    res_model_id=fields.Many2one(
        'ir.model','DocumentModel',
        index=True,ondelete='cascade',required=True)
    res_model=fields.Char(
        'RelatedDocumentModel',
        index=True,related='res_model_id.model',compute_sudo=True,store=True,readonly=True)
    res_id=fields.Many2oneReference(string='RelatedDocumentID',index=True,required=True,model_field='res_model')
    res_name=fields.Char(
        'DocumentName',compute='_compute_res_name',compute_sudo=True,store=True,
        help="Displaynameoftherelateddocument.",readonly=True)
    #activity
    activity_type_id=fields.Many2one(
        'mail.activity.type',string='ActivityType',
        domain="['|',('res_model_id','=',False),('res_model_id','=',res_model_id)]",ondelete='restrict',
        default=_default_activity_type_id)
    activity_category=fields.Selection(related='activity_type_id.category',readonly=True)
    activity_decoration=fields.Selection(related='activity_type_id.decoration_type',readonly=True)
    icon=fields.Char('Icon',related='activity_type_id.icon',readonly=True)
    summary=fields.Char('Summary')
    note=fields.Html('Note',sanitize_style=True)
    date_deadline=fields.Date('DueDate',index=True,required=True,default=fields.Date.context_today)
    automated=fields.Boolean(
        'Automatedactivity',readonly=True,
        help='Indicatesthisactivityhasbeencreatedautomaticallyandnotbyanyuser.')
    #description
    user_id=fields.Many2one(
        'res.users','Assignedto',
        default=lambdaself:self.env.user,
        index=True,required=True)
    request_partner_id=fields.Many2one('res.partner',string='RequestingPartner')
    state=fields.Selection([
        ('overdue','Overdue'),
        ('today','Today'),
        ('planned','Planned')],'State',
        compute='_compute_state')
    recommended_activity_type_id=fields.Many2one('mail.activity.type',string="RecommendedActivityType")
    previous_activity_type_id=fields.Many2one('mail.activity.type',string='PreviousActivityType',readonly=True)
    has_recommended_activities=fields.Boolean(
        'Nextactivitiesavailable',
        compute='_compute_has_recommended_activities',
        help='TechnicalfieldforUXpurpose')
    mail_template_ids=fields.Many2many(related='activity_type_id.mail_template_ids',readonly=True)
    force_next=fields.Boolean(related='activity_type_id.force_next',readonly=True)
    #access
    can_write=fields.Boolean(compute='_compute_can_write',help='Technicalfieldtohidebuttonsifthecurrentuserhasnoaccess.')

    @api.onchange('previous_activity_type_id')
    def_compute_has_recommended_activities(self):
        forrecordinself:
            record.has_recommended_activities=bool(record.previous_activity_type_id.next_type_ids)

    @api.onchange('previous_activity_type_id')
    def_onchange_previous_activity_type_id(self):
        forrecordinself:
            ifrecord.previous_activity_type_id.default_next_type_id:
                record.activity_type_id=record.previous_activity_type_id.default_next_type_id

    @api.depends('res_model','res_id')
    def_compute_res_name(self):
        foractivityinself:
            activity.res_name=activity.res_modeland\
                self.env[activity.res_model].browse(activity.res_id).display_name

    @api.depends('date_deadline')
    def_compute_state(self):
        forrecordinself.filtered(lambdaactivity:activity.date_deadline):
            tz=record.user_id.sudo().tz
            date_deadline=record.date_deadline
            record.state=self._compute_state_from_date(date_deadline,tz)

    @api.model
    def_compute_state_from_date(self,date_deadline,tz=False):
        date_deadline=fields.Date.from_string(date_deadline)
        today_default=date.today()
        today=today_default
        iftz:
            today_utc=pytz.UTC.localize(datetime.utcnow())
            today_tz=today_utc.astimezone(pytz.timezone(tz))
            today=date(year=today_tz.year,month=today_tz.month,day=today_tz.day)
        diff=(date_deadline-today)
        ifdiff.days==0:
            return'today'
        elifdiff.days<0:
            return'overdue'
        else:
            return'planned'

    @api.depends('res_model','res_id','user_id')
    def_compute_can_write(self):
        valid_records=self._filter_access_rules('write')
        forrecordinself:
            record.can_write=recordinvalid_records

    @api.onchange('activity_type_id')
    def_onchange_activity_type_id(self):
        ifself.activity_type_id:
            ifself.activity_type_id.summary:
                self.summary=self.activity_type_id.summary
            self.date_deadline=self._calculate_date_deadline(self.activity_type_id)
            self.user_id=self.activity_type_id.default_user_idorself.env.user
            ifself.activity_type_id.default_description:
                self.note=self.activity_type_id.default_description

    def_calculate_date_deadline(self,activity_type):
        #Date.context_todayiscorrectbecausedate_deadlineisaDateandismeanttobe
        #expressedinuserTZ
        base=fields.Date.context_today(self)
        ifactivity_type.delay_from=='previous_activity'and'activity_previous_deadline'inself.env.context:
            base=fields.Date.from_string(self.env.context.get('activity_previous_deadline'))
        returnbase+relativedelta(**{activity_type.delay_unit:activity_type.delay_count})

    @api.onchange('recommended_activity_type_id')
    def_onchange_recommended_activity_type_id(self):
        ifself.recommended_activity_type_id:
            self.activity_type_id=self.recommended_activity_type_id

    def_filter_access_rules(self,operation):
        #write/unlink:validforcreator/assigned
        ifoperationin('write','unlink'):
            valid=super(MailActivity,self)._filter_access_rules(operation)
            ifvalidandvalid==self:
                returnself
        else:
            valid=self.env[self._name]
        returnself._filter_access_rules_remaining(valid,operation,'_filter_access_rules')

    def_filter_access_rules_python(self,operation):
        #write/unlink:validforcreator/assigned
        ifoperationin('write','unlink'):
            valid=super(MailActivity,self)._filter_access_rules_python(operation)
            ifvalidandvalid==self:
                returnself
        else:
            valid=self.env[self._name]
        returnself._filter_access_rules_remaining(valid,operation,'_filter_access_rules_python')

    def_filter_access_rules_remaining(self,valid,operation,filter_access_rules_method):
        """Returnthesubsetof``self``forwhich``operation``isallowed.
        Acustomimplementationisdoneonactivitiesasthisdocumenthassome
        accessrulesandisbasedonrelateddocumentforactivitiesthatare
        notcoveredbythoserules.

        Accessonactivitiesarethefollowing:

          *create:(``mail_post_access``orwrite)rightonrelateddocuments;
          *read:readrightsonrelateddocuments;
          *write:accessruleOR
                   (``mail_post_access``orwrite)rightsonrelateddocuments);
          *unlink:accessruleOR
                    (``mail_post_access``orwrite)rightsonrelateddocuments);
        """
        #computeremainingforhand-tailoredrules
        remaining=self-valid
        remaining_sudo=remaining.sudo()

        #fallbackonrelateddocumentaccessrightchecks.Usethesameasdefinedformail.thread
        #ifavailable;otherwisefallbackonreadforread,writeforotheroperations.
        activity_to_documents=dict()
        foractivityinremaining_sudo:
            #write/unlink:ifnotupdatingselforassigned,limittoautomatedactivitiestoavoid
            #updatingotherpeople'sactivities.Asunlinkingadocumentbypassesaccessrightschecks
            #onrelatedactivitiesthiswillnotpreventpeoplefromdeletingdocumentswithactivities
            #create/read:justcheckrightsonrelateddocument
            activity_to_documents.setdefault(activity.res_model,list()).append(activity.res_id)
        fordoc_model,doc_idsinactivity_to_documents.items():
            ifhasattr(self.env[doc_model],'_mail_post_access'):
                doc_operation=self.env[doc_model]._mail_post_access
            elifoperation=='read':
                doc_operation='read'
            else:
                doc_operation='write'
            right=self.env[doc_model].check_access_rights(doc_operation,raise_exception=False)
            ifright:
                valid_doc_ids=getattr(self.env[doc_model].browse(doc_ids),filter_access_rules_method)(doc_operation)
                valid+=remaining.filtered(lambdaactivity:activity.res_model==doc_modelandactivity.res_idinvalid_doc_ids.ids)

        returnvalid

    def_check_access_assignation(self):
        """Checkassigneduser(user_idfield)hasaccesstothedocument.Purpose
        istoallowassignedusertohandletheiractivities.Forthatpurpose
        assignedusershouldbeabletoatleastreadthedocument.Wetherefore
        raiseanUserErroriftheassigneduserhasnoaccesstothedocument."""
        foractivityinself:
            model=self.env[activity.res_model].with_user(activity.user_id).with_context(allowed_company_ids=activity.user_id.company_ids.ids)
            try:
                model.check_access_rights('read')
            exceptexceptions.AccessError:
                raiseexceptions.UserError(
                    _('Assigneduser%shasnoaccesstothedocumentandisnotabletohandlethisactivity.')%
                    activity.user_id.display_name)
            else:
                try:
                    target_user=activity.user_id
                    target_record=self.env[activity.res_model].browse(activity.res_id)
                    ifhasattr(target_record,'company_id')and(
                        target_record.company_id!=target_user.company_idand(
                            len(target_user.sudo().company_ids)>1)):
                        return #inthatcaseweskipthecheck,assumingitwouldfailbecauseofthecompany
                    model.browse(activity.res_id).check_access_rule('read')
                exceptexceptions.AccessError:
                    raiseexceptions.UserError(
                        _('Assigneduser%shasnoaccesstothedocumentandisnotabletohandlethisactivity.')%
                        activity.user_id.display_name)

    #------------------------------------------------------
    #ORMoverrides
    #------------------------------------------------------

    @api.model
    defcreate(self,values):
        activity=super(MailActivity,self).create(values)
        need_sudo=False
        try: #inmulticompany,readingthepartnermightbreak
            partner_id=activity.user_id.partner_id.id
        exceptexceptions.AccessError:
            need_sudo=True
            partner_id=activity.user_id.sudo().partner_id.id

        #sendanotificationtoassigneduser;incaseofmanuallydoneactivityalsocheck
        #targethasrightsondocumentotherwisewepreventitscreation.Automatedactivities
        #arecheckedsincetheyareintegratedintobusinessflowsthatshouldnotcrash.
        ifactivity.user_id!=self.env.user:
            ifnotactivity.automated:
                activity._check_access_assignation()
            ifnotself.env.context.get('mail_activity_quick_update',False):
                ifneed_sudo:
                    activity.sudo().action_notify()
                else:
                    activity.action_notify()

        self.env[activity.res_model].browse(activity.res_id).message_subscribe(partner_ids=[partner_id])
        ifactivity.date_deadline<=fields.Date.today():
            self.env['bus.bus'].sendone(
                (self._cr.dbname,'res.partner',activity.user_id.partner_id.id),
                {'type':'activity_updated','activity_created':True})
        returnactivity

    defwrite(self,values):
        ifvalues.get('user_id'):
            user_changes=self.filtered(lambdaactivity:activity.user_id.id!=values.get('user_id'))
            pre_responsibles=user_changes.mapped('user_id.partner_id')
        res=super(MailActivity,self).write(values)

        ifvalues.get('user_id'):
            ifvalues['user_id']!=self.env.uid:
                to_check=user_changes.filtered(lambdaact:notact.automated)
                to_check._check_access_assignation()
                ifnotself.env.context.get('mail_activity_quick_update',False):
                    user_changes.action_notify()
            foractivityinuser_changes:
                self.env[activity.res_model].browse(activity.res_id).message_subscribe(partner_ids=[activity.user_id.partner_id.id])
                ifactivity.date_deadline<=fields.Date.today():
                    self.env['bus.bus'].sendone(
                        (self._cr.dbname,'res.partner',activity.user_id.partner_id.id),
                        {'type':'activity_updated','activity_created':True})
            foractivityinuser_changes:
                ifactivity.date_deadline<=fields.Date.today():
                    forpartnerinpre_responsibles:
                        self.env['bus.bus'].sendone(
                            (self._cr.dbname,'res.partner',partner.id),
                            {'type':'activity_updated','activity_deleted':True})
        returnres

    defunlink(self):
        foractivityinself:
            ifactivity.date_deadline<=fields.Date.today():
                self.env['bus.bus'].sendone(
                    (self._cr.dbname,'res.partner',activity.user_id.partner_id.id),
                    {'type':'activity_updated','activity_deleted':True})
        returnsuper(MailActivity,self).unlink()

    defname_get(self):
        res=[]
        forrecordinself:
            name=record.summaryorrecord.activity_type_id.display_name
            res.append((record.id,name))
        returnres

    #------------------------------------------------------
    #BusinessMethods
    #------------------------------------------------------

    defaction_notify(self):
        ifnotself:
            return
        original_context=self.env.context
        body_template=self.env.ref('mail.message_activity_assigned')
        foractivityinself:
            ifactivity.user_id.lang:
                #Sendthenotificationintheassigneduser'slanguage
                self=self.with_context(lang=activity.user_id.lang)
                body_template=body_template.with_context(lang=activity.user_id.lang)
                activity=activity.with_context(lang=activity.user_id.lang)
            model_description=self.env['ir.model']._get(activity.res_model).display_name
            body=body_template._render(
                dict(
                    activity=activity,
                    model_description=model_description,
                    access_link=self.env['mail.thread']._notify_get_action_link('view',model=activity.res_model,res_id=activity.res_id),
                ),
                engine='ir.qweb',
                minimal_qcontext=True
            )
            record=self.env[activity.res_model].browse(activity.res_id)
            ifactivity.user_id:
                record.message_notify(
                    partner_ids=activity.user_id.partner_id.ids,
                    body=body,
                    subject=_('%(activity_name)s:%(summary)sassignedtoyou',
                        activity_name=activity.res_name,
                        summary=activity.summaryoractivity.activity_type_id.name),
                    record_name=activity.res_name,
                    model_description=model_description,
                    email_layout_xmlid='mail.mail_notification_light',
                )
            body_template=body_template.with_context(original_context)
            self=self.with_context(original_context)

    defaction_done(self):
        """Wrapperwithoutfeedbackbecausewebbuttonaddcontextas
        parameter,thereforesettingcontexttofeedback"""
        messages,next_activities=self._action_done()
        returnmessages.idsandmessages.ids[0]orFalse

    defaction_feedback(self,feedback=False,attachment_ids=None):
        self=self.with_context(clean_context(self.env.context))
        messages,next_activities=self._action_done(feedback=feedback,attachment_ids=attachment_ids)
        returnmessages.idsandmessages.ids[0]orFalse

    defaction_done_schedule_next(self):
        """Wrapperwithoutfeedbackbecausewebbuttonaddcontextas
        parameter,thereforesettingcontexttofeedback"""
        returnself.action_feedback_schedule_next()

    defaction_feedback_schedule_next(self,feedback=False):
        ctx=dict(
            clean_context(self.env.context),
            default_previous_activity_type_id=self.activity_type_id.id,
            activity_previous_deadline=self.date_deadline,
            default_res_id=self.res_id,
            default_res_model=self.res_model,
        )
        messages,next_activities=self._action_done(feedback=feedback) #willunlinkactivity,dontaccessselfafterthat
        ifnext_activities:
            returnFalse
        return{
            'name':_('ScheduleanActivity'),
            'context':ctx,
            'view_mode':'form',
            'res_model':'mail.activity',
            'views':[(False,'form')],
            'type':'ir.actions.act_window',
            'target':'new',
        }

    def_action_done(self,feedback=False,attachment_ids=None):
        """Privateimplementationofmarkingactivityasdone:postingamessage,deletingactivity
            (sincedone),andeventuallycreatetheautomaticalnextactivity(dependingonconfig).
            :paramfeedback:optionalfeedbackfromuserwhenmarkingactivityasdone
            :paramattachment_ids:listofir.attachmentidstoattachtothepostedmail.message
            :returns(messages,activities)where
                -messagesisarecordsetofpostedmail.message
                -activitiesisarecordsetofmail.activityofforcedautomicallycreatedactivities
        """
        #markingas'done'
        messages=self.env['mail.message']
        next_activities_values=[]

        #Searchforallattachmentslinkedtotheactivitiesweareabouttounlink.Thisway,we
        #canlinkthemtothemessagepostedandpreventtheirdeletion.
        attachments=self.env['ir.attachment'].search_read([
            ('res_model','=',self._name),
            ('res_id','in',self.ids),
        ],['id','res_id'])

        activity_attachments=defaultdict(list)
        forattachmentinattachments:
            activity_id=attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        foractivityinself:
            #extractvaluetogeneratenextactivities
            ifactivity.force_next:
                Activity=self.env['mail.activity'].with_context(activity_previous_deadline=activity.date_deadline) #contextkeyisrequiredintheonchangetosetdeadline
                vals=Activity.default_get(Activity.fields_get())

                vals.update({
                    'previous_activity_type_id':activity.activity_type_id.id,
                    'res_id':activity.res_id,
                    'res_model':activity.res_model,
                    'res_model_id':self.env['ir.model']._get(activity.res_model).id,
                })
                virtual_activity=Activity.new(vals)
                virtual_activity._onchange_previous_activity_type_id()
                virtual_activity._onchange_activity_type_id()
                next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))

            #postmessageonactivity,beforedeletingit
            record=self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={
                    'activity':activity,
                    'feedback':feedback,
                    'display_assignee':activity.user_id!=self.env.user
                },
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[(4,attachment_id)forattachment_idinattachment_ids]ifattachment_idselse[],
            )

            #Movingtheattachmentsinthemessage
            #TODO:Fixvoidres_idonattachmentwhenyoucreateanactivitywithanimage
            #directly,seeroute/web_editor/attachment/add
            activity_message=record.message_ids[0]
            message_attachments=self.env['ir.attachment'].browse(activity_attachments[activity.id])
            ifmessage_attachments:
                message_attachments.write({
                    'res_id':activity_message.id,
                    'res_model':activity_message._name,
                })
                activity_message.attachment_ids=message_attachments
            messages|=activity_message

        next_activities=self.env['mail.activity'].create(next_activities_values)
        self.unlink() #willunlinkactivity,dontaccess`self`afterthat

        returnmessages,next_activities

    defaction_close_dialog(self):
        return{'type':'ir.actions.act_window_close'}

    defactivity_format(self):
        activities=self.read()
        mail_template_ids=set([template_idforactivityinactivitiesfortemplate_idinactivity["mail_template_ids"]])
        mail_template_info=self.env["mail.template"].browse(mail_template_ids).read(['id','name'])
        mail_template_dict=dict([(mail_template['id'],mail_template)formail_templateinmail_template_info])
        foractivityinactivities:
            activity['mail_template_ids']=[mail_template_dict[mail_template_id]formail_template_idinactivity['mail_template_ids']]
        returnactivities

    @api.model
    defget_activity_data(self,res_model,domain):
        activity_domain=[('res_model','=',res_model)]
        ifdomain:
            res=self.env[res_model].search(domain)
            activity_domain.append(('res_id','in',res.ids))
        grouped_activities=self.env['mail.activity'].read_group(
            activity_domain,
            ['res_id','activity_type_id','ids:array_agg(id)','date_deadline:min(date_deadline)'],
            ['res_id','activity_type_id'],
            lazy=False)
        #filteroutunreadablerecords
        ifnotdomain:
            res_ids=tuple(a['res_id']foraingrouped_activities)
            res=self.env[res_model].search([('id','in',res_ids)])
            grouped_activities=[aforaingrouped_activitiesifa['res_id']inres.ids]
        res_id_to_deadline={}
        activity_data=defaultdict(dict)
        forgroupingrouped_activities:
            res_id=group['res_id']
            activity_type_id=(group.get('activity_type_id')or(False,False))[0]
            res_id_to_deadline[res_id]=group['date_deadline']if(res_idnotinres_id_to_deadlineorgroup['date_deadline']<res_id_to_deadline[res_id])elseres_id_to_deadline[res_id]
            state=self._compute_state_from_date(group['date_deadline'],self.user_id.sudo().tz)
            activity_data[res_id][activity_type_id]={
                'count':group['__count'],
                'ids':group['ids'],
                'state':state,
                'o_closest_deadline':group['date_deadline'],
            }
        activity_type_infos=[]
        activity_type_ids=self.env['mail.activity.type'].search(['|',('res_model_id.model','=',res_model),('res_model_id','=',False)])
        foreleminsorted(activity_type_ids,key=lambdaitem:item.sequence):
            mail_template_info=[]
            formail_template_idinelem.mail_template_ids:
                mail_template_info.append({"id":mail_template_id.id,"name":mail_template_id.name})
            activity_type_infos.append([elem.id,elem.name,mail_template_info])

        return{
            'activity_types':activity_type_infos,
            'activity_res_ids':sorted(res_id_to_deadline,key=lambdaitem:res_id_to_deadline[item]),
            'grouped_activities':activity_data,
        }


classMailActivityMixin(models.AbstractModel):
    """MailActivityMixinisamixinclasstouseifyouwanttoaddactivities
    managementonamodel.Itworkslikethemail.threadmixin.Itdefines
    anactivity_idsone2manyfieldtowardactivitiesusingres_idandres_model_id.
    Variousrelated/computedfieldsarealsoaddedtohaveaglobalstatusof
    activitiesondocuments.

    ActivitiescomewithanewJSwidgetfortheformview.Itisintegratedinthe
    Chatterwidgetalthoughitisaseparatewidget.Itdisplaysactivitieslinked
    tothecurrentrecordandallowtoschedule,editandmarkdoneactivities.
    Justincludefieldactivity_idsinthediv.oe-chattertouseit.

    Thereisalsoakanbanwidgetdefined.Itdefinesasmallwidgettointegrate
    inkanbanvignettes.Itallowtomanageactivitiesdirectlyfromthekanban
    view.Usewidget="kanban_activity"onactivitiy_idsfieldinkanbanviewto
    useit.

    Somecontextkeysallowtocontrolthemixinbehavior.Usethoseinsome
    specificcaseslikeimport

     *``mail_activity_automation_skip``:skipactivitiesautomation;itmeans
       noautomatedactivitieswillbegenerated,updatedorunlinked,allowing
       tosavecomputationandavoidgeneratingunwantedactivities;
    """
    _name='mail.activity.mixin'
    _description='ActivityMixin'

    def_default_activity_type(self):
        """Defineadefaultfallbackactivitytypewhenrequestedxmlidwasn'tfound.

        Canbeoverridentospecifythedefaultactivitytypeofamodel.
        Itisonlycalledininactivity_schedule()fornow.
        """
        returnself.env.ref('mail.mail_activity_data_todo',raise_if_not_found=False)\
            orself.env['mail.activity.type'].search([('res_model','=',self._name)],limit=1)\
            orself.env['mail.activity.type'].search([('res_model_id','=',False)],limit=1)

    activity_ids=fields.One2many(
        'mail.activity','res_id','Activities',
        auto_join=True,
        groups="base.group_user",)
    activity_state=fields.Selection([
        ('overdue','Overdue'),
        ('today','Today'),
        ('planned','Planned')],string='ActivityState',
        compute='_compute_activity_state',
        groups="base.group_user",
        help='Statusbasedonactivities\nOverdue:Duedateisalreadypassed\n'
             'Today:Activitydateistoday\nPlanned:Futureactivities.')
    activity_user_id=fields.Many2one(
        'res.users','ResponsibleUser',
        related='activity_ids.user_id',readonly=False,
        search='_search_activity_user_id',
        groups="base.group_user")
    activity_type_id=fields.Many2one(
        'mail.activity.type','NextActivityType',
        related='activity_ids.activity_type_id',readonly=False,
        search='_search_activity_type_id',
        groups="base.group_user")
    activity_type_icon=fields.Char('ActivityTypeIcon',related='activity_ids.icon')
    activity_date_deadline=fields.Date(
        'NextActivityDeadline',
        compute='_compute_activity_date_deadline',search='_search_activity_date_deadline',
        compute_sudo=False,readonly=True,store=False,
        groups="base.group_user")
    my_activity_date_deadline=fields.Date(
        'MyActivityDeadline',
        compute='_compute_my_activity_date_deadline',search='_search_my_activity_date_deadline',
        compute_sudo=False,readonly=True,groups="base.group_user")
    activity_summary=fields.Char(
        'NextActivitySummary',
        related='activity_ids.summary',readonly=False,
        search='_search_activity_summary',
        groups="base.group_user",)
    activity_exception_decoration=fields.Selection([
        ('warning','Alert'),
        ('danger','Error')],
        compute='_compute_activity_exception_type',
        search='_search_activity_exception_decoration',
        help="Typeoftheexceptionactivityonrecord.")
    activity_exception_icon=fields.Char('Icon',help="Icontoindicateanexceptionactivity.",
        compute='_compute_activity_exception_type')

    @api.depends('activity_ids.activity_type_id.decoration_type','activity_ids.activity_type_id.icon')
    def_compute_activity_exception_type(self):
        #prefetchallactivitytypesforallactivities,thiswillavoidanyqueryinloops
        self.mapped('activity_ids.activity_type_id.decoration_type')

        forrecordinself:
            activity_type_ids=record.activity_ids.mapped('activity_type_id')
            exception_activity_type_id=False
            foractivity_type_idinactivity_type_ids:
                ifactivity_type_id.decoration_type=='danger':
                    exception_activity_type_id=activity_type_id
                    break
                ifactivity_type_id.decoration_type=='warning':
                    exception_activity_type_id=activity_type_id
            record.activity_exception_decoration=exception_activity_type_idandexception_activity_type_id.decoration_type
            record.activity_exception_icon=exception_activity_type_idandexception_activity_type_id.icon

    def_search_activity_exception_decoration(self,operator,operand):
        return[('activity_ids.activity_type_id.decoration_type',operator,operand)]

    @api.depends('activity_ids.state')
    def_compute_activity_state(self):
        forrecordinself:
            states=record.activity_ids.mapped('state')
            if'overdue'instates:
                record.activity_state='overdue'
            elif'today'instates:
                record.activity_state='today'
            elif'planned'instates:
                record.activity_state='planned'
            else:
                record.activity_state=False

    @api.depends('activity_ids.date_deadline')
    def_compute_activity_date_deadline(self):
        forrecordinself:
            record.activity_date_deadline=record.activity_ids[:1].date_deadline

    def_search_activity_date_deadline(self,operator,operand):
        ifoperator=='='andnotoperand:
            return[('activity_ids','=',False)]
        return[('activity_ids.date_deadline',operator,operand)]

    @api.model
    def_search_activity_user_id(self,operator,operand):
        return[('activity_ids.user_id',operator,operand)]

    @api.model
    def_search_activity_type_id(self,operator,operand):
        return[('activity_ids.activity_type_id',operator,operand)]

    @api.model
    def_search_activity_summary(self,operator,operand):
        return[('activity_ids.summary',operator,operand)]

    @api.depends('activity_ids.date_deadline','activity_ids.user_id')
    @api.depends_context('uid')
    def_compute_my_activity_date_deadline(self):
        forrecordinself:
            record.my_activity_date_deadline=next((
                activity.date_deadline
                foractivityinrecord.activity_ids
                ifactivity.user_id.id==record.env.uid
            ),False)

    def_search_my_activity_date_deadline(self,operator,operand):
        activity_ids=self.env['mail.activity']._search([
            ('date_deadline',operator,operand),
            ('res_model','=',self._name),
            ('user_id','=',self.env.user.id)
        ])
        return[('activity_ids','in',activity_ids)]

    defwrite(self,vals):
        #Deleteactivitiesofarchivedrecord.
        if'active'invalsandvals['active']isFalse:
            self.env['mail.activity'].sudo().search(
                [('res_model','=',self._name),('res_id','in',self.ids)]
            ).unlink()
        returnsuper(MailActivityMixin,self).write(vals)

    defunlink(self):
        """Overrideunlinktodeleterecordsactivitiesthrough(res_model,res_id)."""
        record_ids=self.ids
        result=super(MailActivityMixin,self).unlink()
        self.env['mail.activity'].sudo().search(
            [('res_model','=',self._name),('res_id','in',record_ids)]
        ).unlink()
        returnresult

    def_read_progress_bar(self,domain,group_by,progress_bar):
        group_by_fname=group_by.partition(':')[0]
        ifnot(progress_bar['field']=='activity_state'andself._fields[group_by_fname].store):
            returnsuper()._read_progress_bar(domain,group_by,progress_bar)

        #optimizationfor'activity_state'

        #explicitlycheckaccessrights,sincewebypasstheORM
        self.check_access_rights('read')
        self._flush_search(domain,fields=[group_by_fname],order='id')
        self.env['mail.activity'].flush(['res_model','res_id','user_id','date_deadline'])

        query=self._where_calc(domain)
        self._apply_ir_rules(query,'read')
        gb=group_by.partition(':')[0]
        annotated_groupbys=[
            self._read_group_process_groupby(gb,query)
            forgbin[group_by,'activity_state']
        ]
        groupby_dict={gb['groupby']:gbforgbinannotated_groupbys}
        forgbinannotated_groupbys:
            ifgb['field']=='activity_state':
                gb['qualified_field']='"_last_activity_state"."activity_state"'
        groupby_terms,orderby_terms=self._read_group_prepare('activity_state',[],annotated_groupbys,query)
        select_terms=[
            '%sas"%s"'%(gb['qualified_field'],gb['groupby'])
            forgbinannotated_groupbys
        ]
        from_clause,where_clause,where_params=query.get_sql()
        tz=self._context.get('tz')orself.env.user.tzor'UTC'
        select_query="""
            SELECT1ASid,count(*)AS"__count",{fields}
            FROM{from_clause}
            JOIN(
                SELECTres_id,
                CASE
                    WHENmin(date_deadline-(now()ATTIMEZONECOALESCE(res_partner.tz,%s))::date)>0THEN'planned'
                    WHENmin(date_deadline-(now()ATTIMEZONECOALESCE(res_partner.tz,%s))::date)<0THEN'overdue'
                    WHENmin(date_deadline-(now()ATTIMEZONECOALESCE(res_partner.tz,%s))::date)=0THEN'today'
                    ELSEnull
                ENDASactivity_state
                FROMmail_activity
                JOINres_usersON(res_users.id=mail_activity.user_id)
                JOINres_partnerON(res_partner.id=res_users.partner_id)
                WHEREres_model='{model}'
                GROUPBYres_id
            )AS"_last_activity_state"ON("{table}".id="_last_activity_state".res_id)
            WHERE{where_clause}
            GROUPBY{group_by}
        """.format(
            fields=','.join(select_terms),
            from_clause=from_clause,
            model=self._name,
            table=self._table,
            where_clause=where_clauseor'1=1',
            group_by=','.join(groupby_terms),
        )
        self.env.cr.execute(select_query,[tz]*3+where_params)
        fetched_data=self.env.cr.dictfetchall()
        self._read_group_resolve_many2one_fields(fetched_data,annotated_groupbys)
        data=[
            {key:self._read_group_prepare_data(key,val,groupby_dict)
             forkey,valinrow.items()}
            forrowinfetched_data
        ]
        return[
            self._read_group_format_result(vals,annotated_groupbys,[group_by],domain)
            forvalsindata
        ]

    deftoggle_active(self):
        """Beforearchivingtherecordweshouldalsoremoveitsongoing
        activities.Otherwisetheystayinthesystrayandconcerningarchived
        recordsitmakesnosense."""
        record_to_deactivate=self.filtered(lambdarec:rec[rec._active_name])
        ifrecord_to_deactivate:
            #useasudotobypasseveryaccessrights;allactivitiesshouldberemoved
            self.env['mail.activity'].sudo().search([
                ('res_model','=',self._name),
                ('res_id','in',record_to_deactivate.ids)
            ]).unlink()
        returnsuper(MailActivityMixin,self).toggle_active()

    defactivity_send_mail(self,template_id):
        """Automaticallysendanemailbasedonthegivenmail.template,given
        itsID."""
        template=self.env['mail.template'].browse(template_id).exists()
        ifnottemplate:
            returnFalse
        forrecordinself.with_context(mail_post_autofollow=True):
            record.message_post_with_template(
                template_id,
                composition_mode='comment'
            )
        returnTrue

    defactivity_search(self,act_type_xmlids='',user_id=None,additional_domain=None):
        """Searchautomatedactivitiesoncurrentrecordset,givenalistofactivity
        typesxmlIDs.Itisusefulwhendealingwithspecifictypesinvolvedinautomatic
        activitiesmanagement.

        :paramact_type_xmlids:listofactivitytypesxmlIDs
        :paramuser_id:ifset,restricttoactivitiesofthatuser_id;
        :paramadditional_domain:ifset,filteronthatdomain;
        """
        ifself.env.context.get('mail_activity_automation_skip'):
            returnFalse

        Data=self.env['ir.model.data'].sudo()
        activity_types_ids=[type_idfortype_idin(Data.xmlid_to_res_id(xmlid,raise_if_not_found=False)forxmlidinact_type_xmlids)iftype_id]
        ifnotany(activity_types_ids):
            returnFalse

        domain=[
            '&','&','&',
            ('res_model','=',self._name),
            ('res_id','in',self.ids),
            ('automated','=',True),
            ('activity_type_id','in',activity_types_ids)
        ]

        ifuser_id:
            domain=expression.AND([domain,[('user_id','=',user_id)]])
        ifadditional_domain:
            domain=expression.AND([domain,additional_domain])

        returnself.env['mail.activity'].search(domain)

    defactivity_schedule(self,act_type_xmlid='',date_deadline=None,summary='',note='',**act_values):
        """Scheduleanactivityoneachrecordofthecurrentrecordset.
        Thismethodallowtoprovideasparameteract_type_xmlid.Thisisan
        xml_idofactivitytypeinsteadofdirectlygivinganactivity_type_id.
        Itisusefultoavoidhavingvarious"env.ref"inthecodeandallow
        toletthemixinhandleaccessrights.

        :paramdate_deadline:thedaytheactivitymustbescheduledon
        thetimezoneoftheusermustbeconsideredtosetthecorrectdeadline
        """
        ifself.env.context.get('mail_activity_automation_skip'):
            returnFalse

        ifnotdate_deadline:
            date_deadline=fields.Date.context_today(self)
        ifisinstance(date_deadline,datetime):
            _logger.warning("Scheduleddeadlineshouldbeadate(got%s)",date_deadline)
        ifact_type_xmlid:
            activity_type=self.env.ref(act_type_xmlid,raise_if_not_found=False)orself._default_activity_type()
        else:
            activity_type_id=act_values.get('activity_type_id',False)
            activity_type=activity_type_idandself.env['mail.activity.type'].sudo().browse(activity_type_id)

        model_id=self.env['ir.model']._get(self._name).id
        activities=self.env['mail.activity']
        forrecordinself:
            create_vals={
                'activity_type_id':activity_typeandactivity_type.id,
                'summary':summaryoractivity_type.summary,
                'automated':True,
                'note':noteoractivity_type.default_description,
                'date_deadline':date_deadline,
                'res_model_id':model_id,
                'res_id':record.id,
            }
            create_vals.update(act_values)
            ifnotcreate_vals.get('user_id'):
                create_vals['user_id']=activity_type.default_user_id.idorself.env.uid
            activities|=self.env['mail.activity'].create(create_vals)
        returnactivities

    def_activity_schedule_with_view(self,act_type_xmlid='',date_deadline=None,summary='',views_or_xmlid='',render_context=None,**act_values):
        """Helpermethod:Scheduleanactivityoneachrecordofthecurrentrecordset.
        Thismethodallowtothesamemecanismas`activity_schedule`,butprovide
        2additionnalparameters:
        :paramviews_or_xmlid:recordofir.ui.vieworstringrepresentingthexmlid
            oftheqwebtemplatetorender
        :typeviews_or_xmlid:stringorrecordset
        :paramrender_context:thevaluesrequiredtorenderthegivenqwebtemplate
        :typerender_context:dict
        """
        ifself.env.context.get('mail_activity_automation_skip'):
            returnFalse

        render_context=render_contextordict()
        ifisinstance(views_or_xmlid,str):
            views=self.env.ref(views_or_xmlid,raise_if_not_found=False)
        else:
            views=views_or_xmlid
        ifnotviews:
            return
        activities=self.env['mail.activity']
        forrecordinself:
            render_context['object']=record
            note=views._render(render_context,engine='ir.qweb',minimal_qcontext=True)
            activities|=record.activity_schedule(act_type_xmlid=act_type_xmlid,date_deadline=date_deadline,summary=summary,note=note,**act_values)
        returnactivities

    defactivity_reschedule(self,act_type_xmlids,user_id=None,date_deadline=None,new_user_id=None):
        """Reschedulesomeautomatedactivities.Activitiestorescheduleare
        selectedbasedontypexmlidsandoptionallybyuser.Purposeistobe
        ableto

         *updatethedeadlinetodate_deadline;
         *updatetheresponsibletonew_user_id;
        """
        ifself.env.context.get('mail_activity_automation_skip'):
            returnFalse

        Data=self.env['ir.model.data'].sudo()
        activity_types_ids=[Data.xmlid_to_res_id(xmlid,raise_if_not_found=False)forxmlidinact_type_xmlids]
        activity_types_ids=[act_type_idforact_type_idinactivity_types_idsifact_type_id]
        ifnotany(activity_types_ids):
            returnFalse
        activities=self.activity_search(act_type_xmlids,user_id=user_id)
        ifactivities:
            write_vals={}
            ifdate_deadline:
                write_vals['date_deadline']=date_deadline
            ifnew_user_id:
                write_vals['user_id']=new_user_id
            activities.write(write_vals)
        returnactivities

    defactivity_feedback(self,act_type_xmlids,user_id=None,feedback=None):
        """Setactivitiesasdone,limitingtosomeactivitytypesand
        optionallytoagivenuser."""
        ifself.env.context.get('mail_activity_automation_skip'):
            returnFalse

        Data=self.env['ir.model.data'].sudo()
        activity_types_ids=[Data.xmlid_to_res_id(xmlid,raise_if_not_found=False)forxmlidinact_type_xmlids]
        activity_types_ids=[act_type_idforact_type_idinactivity_types_idsifact_type_id]
        ifnotany(activity_types_ids):
            returnFalse
        activities=self.activity_search(act_type_xmlids,user_id=user_id)
        ifactivities:
            activities.action_feedback(feedback=feedback)
        returnTrue

    defactivity_unlink(self,act_type_xmlids,user_id=None):
        """Unlinkactivities,limitingtosomeactivitytypesandoptionally
        toagivenuser."""
        ifself.env.context.get('mail_activity_automation_skip'):
            returnFalse

        Data=self.env['ir.model.data'].sudo()
        activity_types_ids=[Data.xmlid_to_res_id(xmlid,raise_if_not_found=False)forxmlidinact_type_xmlids]
        activity_types_ids=[act_type_idforact_type_idinactivity_types_idsifact_type_id]
        ifnotany(activity_types_ids):
            returnFalse
        self.activity_search(act_type_xmlids,user_id=user_id).unlink()
        returnTrue
