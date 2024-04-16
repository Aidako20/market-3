#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importast
importlogging
importjson
importre

importrequests
importwerkzeug.urls

fromflectraimportapi,fields,models
fromflectra.exceptionsimportRedirectWarning,UserError
fromflectra.tools.translateimport_

fromflectra.addons.google_account.models.google_serviceimportGOOGLE_TOKEN_ENDPOINT,TIMEOUT

fromdatetimeimportdate

_logger=logging.getLogger(__name__)

#GoogleisdepreciatingtheirOOBAuthFlowon3rdOctober2022,theGoogleDrive
#integrationthusbecomeirrelevantafterthatdate.

#https://developers.googleblog.com/2022/02/making-oauth-flows-safer.html#disallowed-oob
GOOGLE_AUTH_DEPRECATION_DATE=date(2022,10,3)


classGoogleDrive(models.Model):

    _name='google.drive.config'
    _description="GoogleDrivetemplatesconfig"

    def_module_deprecated(self):
        returnGOOGLE_AUTH_DEPRECATION_DATE<fields.Date.today()

    defget_google_drive_url(self,res_id,template_id):
        ifself._module_deprecated():
            return

        self.ensure_one()
        self=self.sudo()

        model=self.model_id
        filter_name=self.filter_id.nameifself.filter_idelseFalse
        record=self.env[model.model].browse(res_id).read()[0]
        record.update({
            'model':model.name,
            'filter':filter_name
        })
        name_gdocs=self.name_template
        try:
            name_gdocs=name_gdocs%record
        except:
            raiseUserError(_("AtleastonekeycannotbefoundinyourGoogleDrivenamepattern."))

        attachments=self.env["ir.attachment"].search([('res_model','=',model.model),('name','=',name_gdocs),('res_id','=',res_id)])
        url=False
        ifattachments:
            url=attachments[0].url
        else:
            url=self.copy_doc(res_id,template_id,name_gdocs,model.model).get('url')
        returnurl

    @api.model
    defget_access_token(self,scope=None):
        ifself._module_deprecated():
            return

        Config=self.env['ir.config_parameter'].sudo()
        google_drive_refresh_token=Config.get_param('google_drive_refresh_token')
        user_is_admin=self.env.is_admin()
        ifnotgoogle_drive_refresh_token:
            ifuser_is_admin:
                dummy,action_id=self.env['ir.model.data'].get_object_reference('base_setup','action_general_configuration')
                msg=_("ThereisnorefreshcodesetforGoogleDrive.Youcansetitupfromtheconfigurationpanel.")
                raiseRedirectWarning(msg,action_id,_('Gototheconfigurationpanel'))
            else:
                raiseUserError(_("GoogleDriveisnotyetconfigured.Pleasecontactyouradministrator."))
        google_drive_client_id=Config.get_param('google_drive_client_id')
        google_drive_client_secret=Config.get_param('google_drive_client_secret')
        #ForGettingNewAccessTokenWithhelpofoldRefreshToken
        data={
            'client_id':google_drive_client_id,
            'refresh_token':google_drive_refresh_token,
            'client_secret':google_drive_client_secret,
            'grant_type':"refresh_token",
            'scope':scopeor'https://www.googleapis.com/auth/drive'
        }
        headers={"Content-type":"application/x-www-form-urlencoded"}
        try:
            req=requests.post(GOOGLE_TOKEN_ENDPOINT,data=data,headers=headers,timeout=TIMEOUT)
            req.raise_for_status()
        exceptrequests.HTTPError:
            ifuser_is_admin:
                dummy,action_id=self.env['ir.model.data'].get_object_reference('base_setup','action_general_configuration')
                msg=_("Somethingwentwrongduringthetokengeneration.Pleaserequestagainanauthorizationcode.")
                raiseRedirectWarning(msg,action_id,_('Gototheconfigurationpanel'))
            else:
                raiseUserError(_("GoogleDriveisnotyetconfigured.Pleasecontactyouradministrator."))
        returnreq.json().get('access_token')

    @api.model
    defcopy_doc(self,res_id,template_id,name_gdocs,res_model):
        ifself._module_deprecated():
            return

        google_web_base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_token=self.get_access_token()
        #Copytemplateintodrivewithhelpofnewaccesstoken
        request_url="https://www.googleapis.com/drive/v2/files/%s?fields=parents/id&access_token=%s"%(template_id,access_token)
        headers={"Content-type":"application/x-www-form-urlencoded"}
        try:
            req=requests.get(request_url,headers=headers,timeout=TIMEOUT)
            req.raise_for_status()
            parents_dict=req.json()
        exceptrequests.HTTPError:
            raiseUserError(_("TheGoogleTemplatecannotbefound.Maybeithasbeendeleted."))

        record_url="ClickonlinktoopenRecordinFlectra\n%s/?db=%s#id=%s&model=%s"%(google_web_base_url,self._cr.dbname,res_id,res_model)
        data={
            "title":name_gdocs,
            "description":record_url,
            "parents":parents_dict['parents']
        }
        request_url="https://www.googleapis.com/drive/v2/files/%s/copy?access_token=%s"%(template_id,access_token)
        headers={
            'Content-type':'application/json',
            'Accept':'text/plain'
        }
        #resp,content=Http().request(request_url,"POST",data_json,headers)
        req=requests.post(request_url,data=json.dumps(data),headers=headers,timeout=TIMEOUT)
        req.raise_for_status()
        content=req.json()
        res={}
        ifcontent.get('alternateLink'):
            res['id']=self.env["ir.attachment"].create({
                'res_model':res_model,
                'name':name_gdocs,
                'res_id':res_id,
                'type':'url',
                'url':content['alternateLink']
            }).id
            #Commitinordertoattachthedocumenttothecurrentobjectinstance,evenifthepermissionshasnotbeenwritten.
            self._cr.commit()
            res['url']=content['alternateLink']
            key=self._get_key_from_url(res['url'])
            request_url="https://www.googleapis.com/drive/v2/files/%s/permissions?emailMessage=This+is+a+drive+file+created+by+Flectra&sendNotificationEmails=false&access_token=%s"%(key,access_token)
            data={'role':'writer','type':'anyone','value':'','withLink':True}
            try:
                req=requests.post(request_url,data=json.dumps(data),headers=headers,timeout=TIMEOUT)
                req.raise_for_status()
            exceptrequests.HTTPError:
                raiseself.env['res.config.settings'].get_config_warning(_("Thepermission'reader'for'anyonewiththelink'hasnotbeenwrittenonthedocument"))
            ifself.env.user.email:
                data={'role':'writer','type':'user','value':self.env.user.email}
                try:
                    requests.post(request_url,data=json.dumps(data),headers=headers,timeout=TIMEOUT)
                exceptrequests.HTTPError:
                    pass
        returnres

    @api.model
    defget_google_drive_config(self,res_model,res_id):
        '''
        Functioncalledbythejs,whennogoogledocareyetassociatedwitharecord,withtheaimtocreateone.It
        willfirstseekforagoogle.docs.configassociatedwiththemodel`res_model`tofindoutwhat'sthetemplate
        ofgoogledoctocopy(thisisusefullifyouwanttostartwithanon-emptydocument,atypeoraname
        differentthanthedefaultvalues).Ifnoconfigisassociatedwiththe`res_model`,thenablanktextdocument
        withadefaultnameiscreated.
          :paramres_model:theobjectforwhichthegoogledociscreated
          :paramids:thelistofidsoftheobjectsforwhichthegoogledociscreated.Thislistissupposedtohave
            alengthof1elementonly(batchprocessingisnotsupportedinthecode,thoughnothingreallypreventit)
          :return:theconfigidandconfigname
        '''
        #TODOinmaster:fixmysignatureandmymodel
        ifisinstance(res_model,str):
            res_model=self.env['ir.model'].search([('model','=',res_model)]).id
        ifnotres_id:
            raiseUserError(_("Creatinggoogledrivemayonlybedonebyoneatatime."))
        #checkifamodelisconfiguredwithatemplate
        configs=self.search([('model_id','=',res_model)])
        config_values=[]
        forconfiginconfigs.sudo():
            ifconfig.filter_id:
                ifconfig.filter_id.user_idandconfig.filter_id.user_id.id!=self.env.user.id:
                    #Private
                    continue
                try:
                    domain=[('id','in',[res_id])]+ast.literal_eval(config.filter_id.domain)
                except:
                    raiseUserError(_("Thedocumentfiltermustnotincludeany'dynamic'part,soitshouldnotbebasedonthecurrenttimeorcurrentuser,forexample."))
                additionnal_context=ast.literal_eval(config.filter_id.context)
                google_doc_configs=self.env[config.filter_id.model_id].with_context(**additionnal_context).search(domain)
                ifgoogle_doc_configs:
                    config_values.append({'id':config.id,'name':config.name})
            else:
                config_values.append({'id':config.id,'name':config.name})
        returnconfig_values

    name=fields.Char('TemplateName',required=True)
    model_id=fields.Many2one('ir.model','Model',required=True,ondelete='cascade')
    model=fields.Char('RelatedModel',related='model_id.model',readonly=True)
    filter_id=fields.Many2one('ir.filters','Filter',domain="[('model_id','=',model)]")
    google_drive_template_url=fields.Char('TemplateURL',required=True)
    google_drive_resource_id=fields.Char('ResourceId',compute='_compute_ressource_id')
    google_drive_client_id=fields.Char('GoogleClient',compute='_compute_client_id')
    name_template=fields.Char('GoogleDriveNamePattern',default='Document%(name)s',help='Choosehowthenewgoogledrivewillbenamed,ongoogleside.Eg.gdoc_%(field_name)s',required=True)
    active=fields.Boolean('Active',default=True)

    def_get_key_from_url(self,url):
        word=re.search("(key=|/d/)([A-Za-z0-9-_]+)",url)
        ifword:
            returnword.group(2)
        returnNone

    def_compute_ressource_id(self):
        forrecordinself:
            ifrecord.google_drive_template_url:
                word=self._get_key_from_url(record.google_drive_template_url)
                ifword:
                    record.google_drive_resource_id=word
                else:
                    raiseUserError(_("PleaseenteravalidGoogleDocumentURL."))
            else:
                record.google_drive_resource_id=False

    def_compute_client_id(self):
        google_drive_client_id=self.env['ir.config_parameter'].sudo().get_param('google_drive_client_id')
        forrecordinself:
            record.google_drive_client_id=google_drive_client_id

    @api.onchange('model_id')
    def_onchange_model_id(self):
        ifself.model_id:
            self.model=self.model_id.model
        else:
            self.filter_id=False
            self.model=False

    @api.constrains('model_id','filter_id')
    def_check_model_id(self):
        ifself.filter_idandself.model_id.model!=self.filter_id.model_id:
            returnFalse
        ifself.model_id.modelandself.filter_id:
            #forceanexecutionofthefiltertoverifycompatibility
            self.get_google_drive_config(self.model_id.model,1)
        returnTrue

    defget_google_scope(self):
        return'https://www.googleapis.com/auth/drivehttps://www.googleapis.com/auth/drive.file'
