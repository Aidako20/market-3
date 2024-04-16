#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importjson
importpytz

fromdatetimeimportdatetime
frompsycopg2importIntegrityError
fromwerkzeug.exceptionsimportBadRequest

fromflectraimporthttp,SUPERUSER_ID
fromflectra.httpimportrequest
fromflectra.toolsimportDEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
fromflectra.tools.translateimport_,_lt
fromflectra.exceptionsimportAccessDenied,ValidationError,UserError
fromflectra.addons.base.models.ir_qweb_fieldsimportnl2br
fromflectra.tools.miscimporthmac,consteq


classWebsiteForm(http.Controller):

    @http.route('/website_form/',type='http',auth="public",methods=['POST'],multilang=False)
    defwebsite_form_empty(self,**kwargs):
        #Thisisaworkaroundtodon'taddlanguageprefixto<formaction="/website_form/"...>
        return""

    #Checkandinsertvaluesfromtheformonthemodel<model>
    @http.route('/website_form/<string:model_name>',type='http',auth="public",methods=['POST'],website=True,csrf=False)
    defwebsite_form(self,model_name,**kwargs):
        #PartialCSRFcheck,onlyperformedwhensessionisauthenticated,asthere
        #isnorealriskforunauthenticatedsessionshere.It'sacommoncasefor
        #embeddedformsnow:SameSitepolicyrejectsthecookies,sothesession
        #islost,andtheCSRFcheckfails,breakingthepostfornogoodreason.
        csrf_token=request.params.pop('csrf_token',None)
        ifrequest.session.uidandnotrequest.validate_csrf(csrf_token):
            raiseBadRequest('Sessionexpired(invalidCSRFtoken)')

        try:
            #Theexceptclausebelowshouldnotletwhathasbeendoneinside
            #herebecommitted.Itshouldnoteitherrollbackeverythingin
            #thiscontrollermethod.Instead,weuseasavepointtorollback
            #whathasbeendoneinsidethetryclause.
            withrequest.env.cr.savepoint():
                ifrequest.env['ir.http']._verify_request_recaptcha_token('website_form'):
                    returnself._handle_website_form(model_name,**kwargs)
            error=_("SuspiciousactivitydetectedbyGooglereCaptcha.")
        except(ValidationError,UserError)ase:
            error=e.args[0]
        returnjson.dumps({
            'error':error,
        })

    def_handle_website_form(self,model_name,**kwargs):
        model_record=request.env['ir.model'].sudo().search([('model','=',model_name),('website_form_access','=',True)])
        ifnotmodel_record:
            returnjson.dumps({
                'error':_("Theform'sspecifiedmodeldoesnotexist")
            })

        try:
            data=self.extract_data(model_record,request.params)
        #Ifweencounteranissuewhileextractingdata
        exceptValidationErrorase:
            #Icouldn'tfindacleanerwaytopassdatatoanexception
            returnjson.dumps({'error_fields':e.args[0]})

        try:
            id_record=self.insert_record(request,model_record,data['record'],data['custom'],data.get('meta'))
            ifid_record:
                self.insert_attachment(model_record,id_record,data['attachments'])
                #incaseofanemail,wewanttosenditimmediatelyinsteadofwaiting
                #fortheemailqueuetoprocess
                ifmodel_name=='mail.mail':
                    form_has_email_cc={'email_cc','email_bcc'}&kwargs.keys()or\
                        'email_cc'inkwargs["website_form_signature"]
                    #removetheemail_ccinformationfromthesignature
                    ifkwargs.get("email_to"):
                        kwargs["website_form_signature"]=kwargs["website_form_signature"].split(':')[0]
                        value=kwargs['email_to']+(':email_cc'ifform_has_email_ccelse'')
                        hash_value=hmac(model_record.env,'website_form_signature',value)
                        ifnotconsteq(kwargs["website_form_signature"],hash_value):
                            raiseAccessDenied('invalidwebsite_form_signature')
                    request.env[model_name].sudo().browse(id_record).send()

        #SomefieldshaveadditionalSQLconstraintsthatwecan'tcheckgenerically
        #Ex:crm.lead.probabilitywhichisafloatbetween0and1
        #TODO:Howtogetthenameoftheerroneousfield?
        exceptIntegrityError:
            returnjson.dumps(False)

        request.session['form_builder_model_model']=model_record.model
        request.session['form_builder_model']=model_record.name
        request.session['form_builder_id']=id_record

        returnjson.dumps({'id':id_record})

    #Constantsstringtomakemetadatareadableonatextfield

    _meta_label=_lt("Metadata") #Titleformetadata

    #Dictofdynamicallycalledfiltersfollowingtypeoffieldtobefaulttolerent

    defidentity(self,field_label,field_input):
        returnfield_input

    definteger(self,field_label,field_input):
        returnint(field_input)

    deffloating(self,field_label,field_input):
        returnfloat(field_input)

    defboolean(self,field_label,field_input):
        returnbool(field_input)

    defbinary(self,field_label,field_input):
        returnbase64.b64encode(field_input.read())

    defone2many(self,field_label,field_input):
        return[int(i)foriinfield_input.split(',')]

    defmany2many(self,field_label,field_input,*args):
        return[(args[0]ifargselse(6,0))+(self.one2many(field_label,field_input),)]

    _input_filters={
        'char':identity,
        'text':identity,
        'html':identity,
        'date':identity,
        'datetime':identity,
        'many2one':integer,
        'one2many':one2many,
        'many2many':many2many,
        'selection':identity,
        'boolean':boolean,
        'integer':integer,
        'float':floating,
        'binary':binary,
        'monetary':floating,
    }


    #Extractalldatasentbytheformandsortitsonseveralproperties
    defextract_data(self,model,values):
        dest_model=request.env[model.sudo().model]

        data={
            'record':{},       #Valuestocreaterecord
            'attachments':[], #Attachedfiles
            'custom':'',       #Customfieldsvalues
            'meta':'',        #Addmetadataifenabled
        }

        authorized_fields=model.sudo()._get_form_writable_fields()
        error_fields=[]
        custom_fields=[]

        forfield_name,field_valueinvalues.items():
            #Ifthevalueofthefieldifafile
            ifhasattr(field_value,'filename'):
                #Undofileuploadfieldnameindexing
                field_name=field_name.split('[',1)[0]

                #Ifit'sanactualbinaryfield,converttheinputfile
                #Ifit'snot,we'lluseattachmentsinstead
                iffield_nameinauthorized_fieldsandauthorized_fields[field_name]['type']=='binary':
                    data['record'][field_name]=base64.b64encode(field_value.read())
                    field_value.stream.seek(0)#donotconsumevalueforever
                    ifauthorized_fields[field_name]['manual']andfield_name+"_filename"indest_model:
                        data['record'][field_name+"_filename"]=field_value.filename
                else:
                    field_value.field_name=field_name
                    data['attachments'].append(field_value)

            #Ifit'saknownfield
            eliffield_nameinauthorized_fields:
                try:
                    input_filter=self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name]=input_filter(self,field_name,field_value)
                exceptValueError:
                    error_fields.append(field_name)

            #Ifit'sacustomfield
            eliffield_namenotin('context','website_form_signature'):
                custom_fields.append((field_name,field_value))

        data['custom']="\n".join([u"%s:%s"%vforvincustom_fields])

        #Addmetadataifenabled #ICPforretrocompatibility
        ifrequest.env['ir.config_parameter'].sudo().get_param('website_form_enable_metadata'):
            environ=request.httprequest.headers.environ
            data['meta']+="%s:%s\n%s:%s\n%s:%s\n%s:%s\n"%(
                "IP"               ,environ.get("REMOTE_ADDR"),
                "USER_AGENT"       ,environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE"  ,environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER"          ,environ.get("HTTP_REFERER")
            )

        #Thisfunctioncanbedefinedonanymodeltoprovide
        #amodel-specificfilteringoftherecordvalues
        #Example:
        #defwebsite_form_input_filter(self,values):
        #    values['name']='%s\'sApplication'%values['partner_name']
        #    returnvalues
        ifhasattr(dest_model,"website_form_input_filter"):
            data['record']=dest_model.website_form_input_filter(request,data['record'])

        missing_required_fields=[labelforlabel,fieldinauthorized_fields.items()iffield['required']andnotlabelindata['record']]
        ifany(error_fields):
            raiseValidationError(error_fields+missing_required_fields)

        returndata

    definsert_record(self,request,model,values,custom,meta=None):
        model_name=model.sudo().model
        ifmodel_name=='mail.mail':
            email_from=_('"%sformsubmission"<%s>')%(request.env.company.name,request.env.company.email)
            values.update({'reply_to':values.get('email_from'),'email_from':email_from})
        record=request.env[model_name].with_user(SUPERUSER_ID).with_context(
            mail_create_nosubscribe=True,
            commit_assetsbundle=False,
        ).create(values)

        ifcustomormeta:
            _custom_label="%s\n___________\n\n"%_("OtherInformation:") #Titleforcustomfields
            ifmodel_name=='mail.mail':
                _custom_label="%s\n___________\n\n"%_("Thismessagehasbeenpostedonyourwebsite!")
            default_field=model.website_form_default_field_id
            default_field_data=values.get(default_field.name,'')
            custom_content=(default_field_data+"\n\n"ifdefault_field_dataelse'')\
                           +(_custom_label+custom+"\n\n"ifcustomelse'')\
                           +(self._meta_label+"\n________\n\n"+metaifmetaelse'')

            #Ifthereisadefaultfieldconfiguredforthismodel,useit.
            #Ifthereisn't,putthecustomdatainamessageinstead
            ifdefault_field.name:
                ifdefault_field.ttype=='html'ormodel_name=='mail.mail':
                    custom_content=nl2br(custom_content)
                record.update({default_field.name:custom_content})
            else:
                values={
                    'body':nl2br(custom_content),
                    'model':model_name,
                    'message_type':'comment',
                    'no_auto_thread':False,
                    'res_id':record.id,
                }
                mail_id=request.env['mail.message'].with_user(SUPERUSER_ID).create(values)

        returnrecord.id

    #Linkallfilesattachedontheform
    definsert_attachment(self,model,id_record,files):
        orphan_attachment_ids=[]
        model_name=model.sudo().model
        record=model.env[model_name].browse(id_record)
        authorized_fields=model.sudo()._get_form_writable_fields()
        forfileinfiles:
            custom_field=file.field_namenotinauthorized_fields
            attachment_value={
                'name':file.filename,
                'datas':base64.encodebytes(file.read()),
                'res_model':model_name,
                'res_id':record.id,
            }
            attachment_id=request.env['ir.attachment'].sudo().create(attachment_value)
            ifattachment_idandnotcustom_field:
                record_sudo=record.sudo()
                value=[(4,attachment_id.id)]
                ifrecord_sudo._fields[file.field_name].type=='many2one':
                    value=attachment_id.id
                record_sudo[file.field_name]=value
            else:
                orphan_attachment_ids.append(attachment_id.id)

        ifmodel_name!='mail.mail':
            #Ifsomeattachmentsdidn'tmatchafieldonthemodel,
            #wecreateamail.messagetolinkthemtotherecord
            iforphan_attachment_ids:
                values={
                    'body':_('<p>Attachedfiles:</p>'),
                    'model':model_name,
                    'message_type':'comment',
                    'no_auto_thread':False,
                    'res_id':id_record,
                    'attachment_ids':[(6,0,orphan_attachment_ids)],
                    'subtype_id':request.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
                }
                mail_id=request.env['mail.message'].with_user(SUPERUSER_ID).create(values)
        else:
            #Ifthemodelismail.mailthenwehavenootherchoicebutto
            #attachthecustombinaryfieldfilesontheattachment_idsfield.
            forattachment_id_idinorphan_attachment_ids:
                record.attachment_ids=[(4,attachment_id_id)]
