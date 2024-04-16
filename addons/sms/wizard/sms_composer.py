#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectraimportapi,fields,models,_
fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.exceptionsimportUserError
fromflectra.toolsimporthtml2plaintext,plaintext2html


classSendSMS(models.TransientModel):
    _name='sms.composer'
    _description='SendSMSWizard'

    @api.model
    defdefault_get(self,fields):
        result=super(SendSMS,self).default_get(fields)

        result['res_model']=result.get('res_model')orself.env.context.get('active_model')

        ifnotresult.get('active_domain'):
            result['active_domain']=repr(self.env.context.get('active_domain',[]))
        ifnotresult.get('res_ids'):
            ifnotresult.get('res_id')andself.env.context.get('active_ids')andlen(self.env.context.get('active_ids'))>1:
                result['res_ids']=repr(self.env.context.get('active_ids'))
        ifnotresult.get('res_id'):
            ifnotresult.get('res_ids')andself.env.context.get('active_id'):
                result['res_id']=self.env.context.get('active_id')

        returnresult

    #documents
    composition_mode=fields.Selection([
        ('numbers','Sendtonumbers'),
        ('comment','Postonadocument'),
        ('mass','SendSMSinbatch')],string='CompositionMode',
        compute='_compute_composition_mode',readonly=False,required=True,store=True)
    res_model=fields.Char('DocumentModelName')
    res_id=fields.Integer('DocumentID')
    res_ids=fields.Char('DocumentIDs')
    res_ids_count=fields.Integer(
        'Visiblerecordscount',compute='_compute_recipients_count',compute_sudo=False,
        help='NumberofrecipientsthatwillreceivetheSMSifsentinmassmode,withoutapplyingtheActiveDomainvalue')
    use_active_domain=fields.Boolean('Useactivedomain')
    active_domain=fields.Text('Activedomain',readonly=True)
    active_domain_count=fields.Integer(
        'Activerecordscount',compute='_compute_recipients_count',compute_sudo=False,
        help='NumberofrecordsfoundwhensearchingwiththevalueinActiveDomain')
    comment_single_recipient=fields.Boolean(
        'SingleMode',compute='_compute_comment_single_recipient',compute_sudo=False,
        help='IndicatesiftheSMScomposertargetsasinglespecificrecipient')
    #optionsforcommentandmassmode
    mass_keep_log=fields.Boolean('Keepanoteondocument',default=True)
    mass_force_send=fields.Boolean('Senddirectly',default=False)
    mass_use_blacklist=fields.Boolean('Useblacklist',default=True)
    #recipients
    recipient_valid_count=fields.Integer('#Validrecipients',compute='_compute_recipients',compute_sudo=False)
    recipient_invalid_count=fields.Integer('#Invalidrecipients',compute='_compute_recipients',compute_sudo=False)
    recipient_single_description=fields.Text('Recipients(Partners)',compute='_compute_recipient_single',compute_sudo=False)
    recipient_single_number=fields.Char('StoredRecipientNumber',compute='_compute_recipient_single',compute_sudo=False)
    recipient_single_number_itf=fields.Char(
        'RecipientNumber',compute='_compute_recipient_single',
        readonly=False,compute_sudo=False,store=True,
        help='UXfieldallowingtoedittherecipientnumber.Ifchangeditwillbestoredontotherecipient.')
    recipient_single_valid=fields.Boolean("Isvalid",compute='_compute_recipient_single_valid',compute_sudo=False)
    number_field_name=fields.Char('NumberField')
    numbers=fields.Char('Recipients(Numbers)')
    sanitized_numbers=fields.Char('SanitizedNumber',compute='_compute_sanitized_numbers',compute_sudo=False)
    #content
    template_id=fields.Many2one('sms.template',string='UseTemplate',domain="[('model','=',res_model)]")
    body=fields.Text(
        'Message',compute='_compute_body',
        readonly=False,store=True,required=True)

    @api.depends('res_ids_count','active_domain_count')
    @api.depends_context('sms_composition_mode')
    def_compute_composition_mode(self):
        forcomposerinself:
            ifself.env.context.get('sms_composition_mode')=='guess'ornotcomposer.composition_mode:
                ifcomposer.res_ids_count>1or(composer.use_active_domainandcomposer.active_domain_count>1):
                    composer.composition_mode='mass'
                else:
                    composer.composition_mode='comment'

    @api.depends('res_model','res_id','res_ids','active_domain')
    def_compute_recipients_count(self):
        forcomposerinself:
            composer.res_ids_count=len(literal_eval(composer.res_ids))ifcomposer.res_idselse0
            ifcomposer.res_model:
                composer.active_domain_count=self.env[composer.res_model].search_count(literal_eval(composer.active_domainor'[]'))
            else:
                composer.active_domain_count=0

    @api.depends('res_id','composition_mode')
    def_compute_comment_single_recipient(self):
        forcomposerinself:
            composer.comment_single_recipient=bool(composer.res_idandcomposer.composition_mode=='comment')

    @api.depends('res_model','res_id','res_ids','use_active_domain','composition_mode','number_field_name','sanitized_numbers')
    def_compute_recipients(self):
        forcomposerinself:
            composer.recipient_valid_count=0
            composer.recipient_invalid_count=0

            ifcomposer.composition_modenotin('comment','mass')ornotcomposer.res_model:
                continue

            records=composer._get_records()
            ifrecordsandisinstance(records,self.pool['mail.thread']):
                res=records._sms_get_recipients_info(force_field=composer.number_field_name,partner_fallback=notcomposer.comment_single_recipient)
                composer.recipient_valid_count=len([ridforrid,rvaluesinres.items()ifrvalues['sanitized']])
                composer.recipient_invalid_count=len([ridforrid,rvaluesinres.items()ifnotrvalues['sanitized']])
            else:
                composer.recipient_invalid_count=0if(
                    composer.sanitized_numbersor(composer.composition_mode=='mass'andcomposer.use_active_domain)
                )else1

    @api.depends('res_model','number_field_name')
    def_compute_recipient_single(self):
        forcomposerinself:
            records=composer._get_records()
            ifnotrecordsornotisinstance(records,self.pool['mail.thread'])ornotcomposer.comment_single_recipient:
                composer.recipient_single_description=False
                composer.recipient_single_number=''
                composer.recipient_single_number_itf=''
                continue
            records.ensure_one()
            res=records._sms_get_recipients_info(force_field=composer.number_field_name,partner_fallback=True)
            composer.recipient_single_description=res[records.id]['partner'].nameorrecords._sms_get_default_partners().display_name
            composer.recipient_single_number=res[records.id]['number']or''
            ifnotcomposer.recipient_single_number_itf:
                composer.recipient_single_number_itf=res[records.id]['number']or''
            ifnotcomposer.number_field_name:
                composer.number_field_name=res[records.id]['field_store']

    @api.depends('recipient_single_number','recipient_single_number_itf')
    def_compute_recipient_single_valid(self):
        forcomposerinself:
            value=composer.recipient_single_number_itforcomposer.recipient_single_number
            ifvalue:
                records=composer._get_records()
                sanitized=phone_validation.phone_sanitize_numbers_w_record([value],records)[value]['sanitized']
                composer.recipient_single_valid=bool(sanitized)
            else:
                composer.recipient_single_valid=False

    @api.depends('numbers','res_model','res_id')
    def_compute_sanitized_numbers(self):
        forcomposerinself:
            ifcomposer.numbers:
                record=composer._get_records()ifcomposer.res_modelandcomposer.res_idelseself.env.user
                numbers=[number.strip()fornumberincomposer.numbers.split(',')]
                sanitize_res=phone_validation.phone_sanitize_numbers_w_record(numbers,record)
                sanitized_numbers=[info['sanitized']forinfoinsanitize_res.values()ifinfo['sanitized']]
                invalid_numbers=[numberfornumber,infoinsanitize_res.items()ifinfo['code']]
                ifinvalid_numbers:
                    raiseUserError(_('Followingnumbersarenotcorrectlyencoded:%s',repr(invalid_numbers)))
                composer.sanitized_numbers=','.join(sanitized_numbers)
            else:
                composer.sanitized_numbers=False

    @api.depends('composition_mode','res_model','res_id','template_id')
    def_compute_body(self):
        forrecordinself:
            ifrecord.template_idandrecord.composition_mode=='comment'andrecord.res_id:
                record.body=record.template_id._render_field('body',[record.res_id],compute_lang=True)[record.res_id]
            elifrecord.template_id:
                record.body=record.template_id.body

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model
    defcreate(self,values):
        #TDEFIXME:currentlyhavetocomputemanuallytoavoidrequiredissue,waitingVFEbranch
        ifnotvalues.get('body')ornotvalues.get('composition_mode'):
            values_wdef=self._add_missing_default_values(values)
            cache_composer=self.new(values_wdef)
            cache_composer._compute_body()
            cache_composer._compute_composition_mode()
            values['body']=values.get('body')orcache_composer.body
            values['composition_mode']=values.get('composition_mode')orcache_composer.composition_mode
        returnsuper(SendSMS,self).create(values)

    #------------------------------------------------------------
    #Actions
    #------------------------------------------------------------

    defaction_send_sms(self):
        ifself.composition_modein('numbers','comment'):
            ifself.comment_single_recipientandnotself.recipient_single_valid:
                raiseUserError(_('Invalidrecipientnumber.Pleaseupdateit.'))
            elifnotself.comment_single_recipientandself.recipient_invalid_count:
                raiseUserError(_('%sinvalidrecipients',self.recipient_invalid_count))
        self._action_send_sms()
        returnFalse

    defaction_send_sms_mass_now(self):
        ifnotself.mass_force_send:
            self.write({'mass_force_send':True})
        returnself.action_send_sms()

    def_action_send_sms(self):
        records=self._get_records()
        ifself.composition_mode=='numbers':
            returnself._action_send_sms_numbers()
        elifself.composition_mode=='comment':
            ifrecordsisNoneornotisinstance(records,self.pool['mail.thread']):
                returnself._action_send_sms_numbers()
            ifself.comment_single_recipient:
                returnself._action_send_sms_comment_single(records)
            else:
                returnself._action_send_sms_comment(records)
        else:
            returnself._action_send_sms_mass(records)

    def_action_send_sms_numbers(self):
        self.env['sms.api']._send_sms_batch([{
            'res_id':0,
            'number':number,
            'content':self.body,
        }fornumberinself.sanitized_numbers.split(',')])
        returnTrue

    def_action_send_sms_comment_single(self,records=None):
        #Ifwehavearecipient_single_originalnumber,it'spossiblethisnumberhasbeencorrectedinthepopup
        #ifinvalid.Asaconsequence,thetestcannotbebasedonrecipient_invalid_count,whichcountisbased
        #onthenumbersinthedatabase.
        records=recordsifrecordsisnotNoneelseself._get_records()
        records.ensure_one()
        ifnotself.number_field_name:
            self.numbers=self.recipient_single_number_itforself.recipient_single_number
        elifself.recipient_single_number_itfandself.recipient_single_number_itf!=self.recipient_single_number:
            records.write({self.number_field_name:self.recipient_single_number_itf})
        returnself._action_send_sms_comment(records=records)

    def_action_send_sms_comment(self,records=None):
        records=recordsifrecordsisnotNoneelseself._get_records()
        subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        messages=self.env['mail.message']
        all_bodies=self._prepare_body_values(records)

        forrecordinrecords:
            messages+=record._message_sms(
                all_bodies[record.id],
                subtype_id=subtype_id,
                number_field=self.number_field_name,
                sms_numbers=self.sanitized_numbers.split(',')ifself.sanitized_numberselseNone)
        returnmessages

    def_action_send_sms_mass(self,records=None):
        records=recordsifrecordsisnotNoneelseself._get_records()

        sms_record_values=self._prepare_mass_sms_values(records)
        sms_all=self._prepare_mass_sms(records,sms_record_values)

        ifsms_allandself.mass_keep_logandrecordsandisinstance(records,self.pool['mail.thread']):
            log_values=self._prepare_mass_log_values(records,sms_record_values)
            records._message_log_batch(**log_values)

        ifsms_allandself.mass_force_send:
            sms_all.filtered(lambdasms:sms.state=='outgoing').send(auto_commit=False,raise_exception=False)
            returnself.env['sms.sms'].sudo().search([('id','in',sms_all.ids)])
        returnsms_all

    #------------------------------------------------------------
    #Massmodespecific
    #------------------------------------------------------------

    def_get_blacklist_record_ids(self,records,recipients_info):
        """Getalistofblacklistedrecords.Thosewillbedirectlycanceled
        withtherighterrorcode."""
        ifself.mass_use_blacklist:
            bl_numbers=self.env['phone.blacklist'].sudo().search([]).mapped('number')
            return[r.idforrinrecordsifrecipients_info[r.id]['sanitized']inbl_numbers]
        return[]

    def_get_done_record_ids(self,records,recipients_info):
        """Getalistofalready-donerecords.Orderofrecordsetisusedto
        spotduplicatessopayattentiontoitifnecessary."""
        done_ids,done=[],[]
        forrecordinrecords:
            sanitized=recipients_info[record.id]['sanitized']
            ifsanitizedindone:
                done_ids.append(record.id)
            else:
                done.append(sanitized)
        returndone_ids

    def_prepare_recipient_values(self,records):
        recipients_info=records._sms_get_recipients_info(force_field=self.number_field_name)
        returnrecipients_info

    def_prepare_body_values(self,records):
        ifself.template_idandself.body==self.template_id.body:
            all_bodies=self.template_id._render_field('body',records.ids,compute_lang=True)
        else:
            all_bodies=self.env['mail.render.mixin']._render_template(self.body,records._name,records.ids)
        returnall_bodies

    def_prepare_mass_sms_values(self,records):
        all_bodies=self._prepare_body_values(records)
        all_recipients=self._prepare_recipient_values(records)
        blacklist_ids=self._get_blacklist_record_ids(records,all_recipients)
        done_ids=self._get_done_record_ids(records,all_recipients)

        result={}
        forrecordinrecords:
            recipients=all_recipients[record.id]
            sanitized=recipients['sanitized']
            ifsanitizedandrecord.idinblacklist_ids:
                state='canceled'
                error_code='sms_blacklist'
            elifsanitizedandrecord.idindone_ids:
                state='canceled'
                error_code='sms_duplicate'
            elifnotsanitized:
                state='error'
                error_code='sms_number_format'ifrecipients['number']else'sms_number_missing'
            else:
                state='outgoing'
                error_code=''

            result[record.id]={
                'body':all_bodies[record.id],
                'partner_id':recipients['partner'].id,
                'number':sanitizedifsanitizedelserecipients['number'],
                'state':state,
                'error_code':error_code,
            }
        returnresult

    def_prepare_mass_sms(self,records,sms_record_values):
        sms_create_vals=[sms_record_values[record.id]forrecordinrecords]
        returnself.env['sms.sms'].sudo().create(sms_create_vals)

    def_prepare_log_body_values(self,sms_records_values):
        result={}
        forrecord_id,sms_valuesinsms_records_values.items():
            result[record_id]=plaintext2html(html2plaintext(sms_values['body']))
        returnresult

    def_prepare_mass_log_values(self,records,sms_records_values):
        return{
            'bodies':self._prepare_log_body_values(sms_records_values),
            'message_type':'sms',
        }

    #------------------------------------------------------------
    #Tools
    #------------------------------------------------------------

    def_get_composer_values(self,composition_mode,res_model,res_id,body,template_id):
        result={}
        ifcomposition_mode=='comment':
            ifnotbodyandtemplate_idandres_id:
                template=self.env['sms.template'].browse(template_id)
                result['body']=template._render_template(template.body,res_model,[res_id])[res_id]
            eliftemplate_id:
                template=self.env['sms.template'].browse(template_id)
                result['body']=template.body
        else:
            ifnotbodyandtemplate_id:
                template=self.env['sms.template'].browse(template_id)
                result['body']=template.body
        returnresult

    def_get_records(self):
        ifnotself.res_model:
            returnNone
        ifself.use_active_domain:
            active_domain=literal_eval(self.active_domainor'[]')
            records=self.env[self.res_model].search(active_domain)
        elifself.res_ids:
            records=self.env[self.res_model].browse(literal_eval(self.res_ids))
        elifself.res_id:
            records=self.env[self.res_model].browse(self.res_id)
        else:
            records=self.env[self.res_model]

        records=records.with_context(mail_notify_author=True)
        returnrecords
