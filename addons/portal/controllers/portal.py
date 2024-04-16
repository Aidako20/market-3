#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importfunctools
importjson
importlogging
importmath
importre

fromwerkzeugimporturls

fromflectraimportfieldsasflectra_fields,http,tools,_,SUPERUSER_ID
fromflectra.exceptionsimportValidationError,AccessError,MissingError,UserError,AccessDenied
fromflectra.httpimportcontent_disposition,Controller,request,route
fromflectra.toolsimportconsteq

#--------------------------------------------------
#Misctools
#--------------------------------------------------

_logger=logging.getLogger(__name__)
defpager(url,total,page=1,step=30,scope=5,url_args=None):
    """Generateadictwithrequiredvaluetorender`website.pager`template.Thismethodcompute
        url,pagerangetodisplay,...inthepager.
        :paramurl:baseurlofthepagelink
        :paramtotal:numbertotalofitemtobesplittedintopages
        :parampage:currentpage
        :paramstep:itemperpage
        :paramscope:numberofpagetodisplayonpager
        :paramurl_args:additionnalparameterstoaddasqueryparamstopageurl
        :typeurl_args:dict
        :returnsdict
    """
    #ComputePager
    page_count=int(math.ceil(float(total)/step))

    page=max(1,min(int(pageifstr(page).isdigit()else1),page_count))
    scope-=1

    pmin=max(page-int(math.floor(scope/2)),1)
    pmax=min(pmin+scope,page_count)

    ifpmax-pmin<scope:
        pmin=pmax-scopeifpmax-scope>0else1

    defget_url(page):
        _url="%s/page/%s"%(url,page)ifpage>1elseurl
        ifurl_args:
            _url="%s?%s"%(_url,urls.url_encode(url_args))
        return_url

    return{
        "page_count":page_count,
        "offset":(page-1)*step,
        "page":{
            'url':get_url(page),
            'num':page
        },
        "page_first":{
            'url':get_url(1),
            'num':1
        },
        "page_start":{
            'url':get_url(pmin),
            'num':pmin
        },
        "page_previous":{
            'url':get_url(max(pmin,page-1)),
            'num':max(pmin,page-1)
        },
        "page_next":{
            'url':get_url(min(pmax,page+1)),
            'num':min(pmax,page+1)
        },
        "page_end":{
            'url':get_url(pmax),
            'num':pmax
        },
        "page_last":{
            'url':get_url(page_count),
            'num':page_count
        },
        "pages":[
            {'url':get_url(page_num),'num':page_num}forpage_numinrange(pmin,pmax+1)
        ]
    }


defget_records_pager(ids,current):
    ifcurrent.idinidsand(hasattr(current,'website_url')orhasattr(current,'access_url')):
        attr_name='access_url'ifhasattr(current,'access_url')else'website_url'
        idx=ids.index(current.id)
        prev_record=idx!=0andcurrent.browse(ids[idx-1])
        next_record=idx<len(ids)-1andcurrent.browse(ids[idx+1])

        ifprev_recordandprev_record[attr_name]andattr_name=="access_url":
            prev_url='%s?access_token=%s'%(prev_record[attr_name],prev_record._portal_ensure_token())
        elifprev_recordandprev_record[attr_name]:
            prev_url=prev_record[attr_name]
        else:
            prev_url=prev_record

        ifnext_recordandnext_record[attr_name]andattr_name=="access_url":
            next_url='%s?access_token=%s'%(next_record[attr_name],next_record._portal_ensure_token())
        elifnext_recordandnext_record[attr_name]:
            next_url=next_record[attr_name]
        else:
            next_url=next_record

        return{
            'prev_record':prev_url,
            'next_record':next_url,
        }
    return{}


def_build_url_w_params(url_string,query_params,remove_duplicates=True):
    """Rebuildastringurlbasedonurl_stringandcorrectlycomputequeryparameters
    usingthosepresentintheurlandthosegivenbyquery_params.Havingduplicatesin
    thefinalurlisoptional.Forexample:

     *url_string='/my?foo=bar&error=pay'
     *query_params={'foo':'bar2','alice':'bob'}
     *ifremoveduplicates:result='/my?foo=bar2&error=pay&alice=bob'
     *else:result='/my?foo=bar&foo=bar2&error=pay&alice=bob'
    """
    url=urls.url_parse(url_string)
    url_params=url.decode_query()
    ifremove_duplicates: #converttostandarddictinsteadofwerkzeugmultidicttoremoveduplicatesautomatically
        url_params=url_params.to_dict()
    url_params.update(query_params)
    returnurl.replace(query=urls.url_encode(url_params)).to_url()


classCustomerPortal(Controller):

    MANDATORY_BILLING_FIELDS=["name","phone","email","street","city","country_id"]
    OPTIONAL_BILLING_FIELDS=["zipcode","state_id","vat","company_name"]

    _items_per_page=20

    def_prepare_portal_layout_values(self):
        """Valuesfor/my/*templatesrendering.

        Doesnotincludetherecordcounts.
        """
        #getcustomersalesrep
        sales_user=False
        partner=request.env.user.partner_id
        ifpartner.user_idandnotpartner.user_id._is_public():
            sales_user=partner.user_id

        return{
            'sales_user':sales_user,
            'page_name':'home',
        }

    def_prepare_home_portal_values(self,counters):
        """Valuesfor/my&/my/homeroutestemplaterendering.

        Includestherecordcountforthedisplayedbadges.
        where'coutners'isthelistofthedisplayedbadges
        andsothelisttocompute.
        """
        return{}

    @route(['/my/counters'],type='json',auth="user",website=True)
    defcounters(self,counters,**kw):
        returnself._prepare_home_portal_values(counters)

    @route(['/my','/my/home'],type='http',auth="user",website=True)
    defhome(self,**kw):
        values=self._prepare_portal_layout_values()
        returnrequest.render("portal.portal_my_home",values)

    @route(['/my/account'],type='http',auth='user',website=True)
    defaccount(self,redirect=None,**post):
        values=self._prepare_portal_layout_values()
        partner=request.env.user.partner_id
        values.update({
            'error':{},
            'error_message':[],
        })

        ifpostandrequest.httprequest.method=='POST':
            error,error_message=self.details_form_validate(post)
            values.update({'error':error,'error_message':error_message})
            values.update(post)
            ifnoterror:
                values={key:post[key]forkeyinself.MANDATORY_BILLING_FIELDS}
                values.update({key:post[key]forkeyinself.OPTIONAL_BILLING_FIELDSifkeyinpost})
                forfieldinset(['country_id','state_id'])&set(values.keys()):
                    try:
                        values[field]=int(values[field])
                    except:
                        values[field]=False
                values.update({'zip':values.pop('zipcode','')})
                partner.sudo().write(values)
                ifredirect:
                    returnrequest.redirect(redirect)
                returnrequest.redirect('/my/home')

        countries=request.env['res.country'].sudo().search([])
        states=request.env['res.country.state'].sudo().search([])

        values.update({
            'partner':partner,
            'countries':countries,
            'states':states,
            'has_check_vat':hasattr(request.env['res.partner'],'check_vat'),
            'redirect':redirect,
            'page_name':'my_details',
        })

        response=request.render("portal.portal_my_details",values)
        response.headers['X-Frame-Options']='DENY'
        returnresponse

    @route('/my/security',type='http',auth='user',website=True,methods=['GET','POST'])
    defsecurity(self,**post):
        values=self._prepare_portal_layout_values()
        values['get_error']=get_error

        ifrequest.httprequest.method=='POST':
            values.update(self._update_password(
                post['old'].strip(),
                post['new1'].strip(),
                post['new2'].strip()
            ))

        returnrequest.render('portal.portal_my_security',values,headers={
            'X-Frame-Options':'DENY'
        })

    def_update_password(self,old,new1,new2):
        fork,vin[('old',old),('new1',new1),('new2',new2)]:
            ifnotv:
                return{'errors':{'password':{k:_("Youcannotleaveanypasswordempty.")}}}

        ifnew1!=new2:
            return{'errors':{'password':{'new2':_("Thenewpasswordanditsconfirmationmustbeidentical.")}}}

        try:
            request.env['res.users'].change_password(old,new1)
        exceptUserErrorase:
            return{'errors':{'password':e.name}}
        exceptAccessDeniedase:
            msg=e.args[0]
            ifmsg==AccessDenied().args[0]:
                msg=_('Theoldpasswordyouprovidedisincorrect,yourpasswordwasnotchanged.')
            return{'errors':{'password':{'old':msg}}}

        #updatesessiontokensotheuserdoesnotgetloggedout(cacheclearedbypasswdchange)
        new_token=request.env.user._compute_session_token(request.session.sid)
        request.session.session_token=new_token

        return{'success':{'password':True}}

    @http.route('/portal/attachment/add',type='http',auth='public',methods=['POST'],website=True)
    defattachment_add(self,name,file,res_model,res_id,access_token=None,**kwargs):
        """Processafileuploadedfromtheportalchatterandcreatethe
        corresponding`ir.attachment`.

        Theattachmentwillbecreated"pending"untiltheassociatedmessage
        isactuallycreated,anditwillbegarbagecollectedotherwise.

        :paramname:nameofthefiletosave.
        :typename:string

        :paramfile:thefiletosave
        :typefile:werkzeug.FileStorage

        :paramres_model:nameofthemodeloftheoriginaldocument.
            Tocheckaccessrightsonly,itwillnotbesavedhere.
        :typeres_model:string

        :paramres_id:idoftheoriginaldocument.
            Tocheckaccessrightsonly,itwillnotbesavedhere.
        :typeres_id:int

        :paramaccess_token:access_tokenoftheoriginaldocument.
            Tocheckaccessrightsonly,itwillnotbesavedhere.
        :typeaccess_token:string

        :return:attachmentdata{id,name,mimetype,file_size,access_token}
        :rtype:dict
        """
        try:
            self._document_check_access(res_model,int(res_id),access_token=access_token)
        except(AccessError,MissingError)ase:
            raiseUserError(_("Thedocumentdoesnotexistoryoudonothavetherightstoaccessit."))

        IrAttachment=request.env['ir.attachment']
        access_token=False

        #Avoidusingsudoorcreatingaccess_tokenwhennotnecessary:internal
        #userscancreateattachments,asopposedtopublicandportalusers.
        ifnotrequest.env.user.has_group('base.group_user'):
            IrAttachment=IrAttachment.sudo().with_context(binary_field_real_user=IrAttachment.env.user)
            access_token=IrAttachment._generate_access_token()

        #Atthispointtherelatedmessagedoesnotexistyet,soweassign
        #thosespecificres_modelandres_is.Theywillbecorrectlyset
        #whenthemessageiscreated:see`portal_chatter_post`,
        #orgarbagecollectedotherwise:see `_garbage_collect_attachments`.
        attachment=IrAttachment.create({
            'name':name,
            'datas':base64.b64encode(file.read()),
            'res_model':'mail.compose.message',
            'res_id':0,
            'access_token':access_token,
        })
        returnrequest.make_response(
            data=json.dumps(attachment.read(['id','name','mimetype','file_size','access_token'])[0]),
            headers=[('Content-Type','application/json')]
        )

    @http.route('/portal/attachment/remove',type='json',auth='public')
    defattachment_remove(self,attachment_id,access_token=None):
        """Removethegiven`attachment_id`,onlyifitisina"pending"state.

        Theusermusthaveaccessrightontheattachmentorprovideavalid
        `access_token`.
        """
        try:
            attachment_sudo=self._document_check_access('ir.attachment',int(attachment_id),access_token=access_token)
        except(AccessError,MissingError)ase:
            raiseUserError(_("Theattachmentdoesnotexistoryoudonothavetherightstoaccessit."))

        ifattachment_sudo.res_model!='mail.compose.message'orattachment_sudo.res_id!=0:
            raiseUserError(_("Theattachment%scannotberemovedbecauseitisnotinapendingstate.",attachment_sudo.name))

        ifattachment_sudo.env['mail.message'].search([('attachment_ids','in',attachment_sudo.ids)]):
            raiseUserError(_("Theattachment%scannotberemovedbecauseitislinkedtoamessage.",attachment_sudo.name))

        returnattachment_sudo.unlink()

    defdetails_form_validate(self,data):
        error=dict()
        error_message=[]

        #Validation
        forfield_nameinself.MANDATORY_BILLING_FIELDS:
            ifnotdata.get(field_name):
                error[field_name]='missing'

        #emailvalidation
        ifdata.get('email')andnottools.single_email_re.match(data.get('email')):
            error["email"]='error'
            error_message.append(_('InvalidEmail!Pleaseenteravalidemailaddress.'))

        #vatvalidation
        partner=request.env.user.partner_id
        ifdata.get("vat")andpartnerandpartner.vat!=data.get("vat"):
            ifpartner.can_edit_vat():
                ifhasattr(partner,"check_vat"):
                    ifdata.get("country_id"):
                        data["vat"]=request.env["res.partner"].fix_eu_vat_number(int(data.get("country_id")),data.get("vat"))
                    partner_dummy=partner.new({
                        'vat':data['vat'],
                        'country_id':(int(data['country_id'])
                                       ifdata.get('country_id')elseFalse),
                    })
                    try:
                        partner_dummy.check_vat()
                    exceptValidationError:
                        error["vat"]='error'
            else:
                error_message.append(_('ChangingVATnumberisnotallowedoncedocument(s)havebeenissuedforyouraccount.Pleasecontactusdirectlyforthisoperation.'))

        #errormessageforemptyrequiredfields
        if[errforerrinerror.values()iferr=='missing']:
            error_message.append(_('Somerequiredfieldsareempty.'))

        unknown=[kforkindataifknotinself.MANDATORY_BILLING_FIELDS+self.OPTIONAL_BILLING_FIELDS]
        ifunknown:
            error['common']='Unknownfield'
            error_message.append("Unknownfield'%s'"%','.join(unknown))

        returnerror,error_message

    def_document_check_access(self,model_name,document_id,access_token=None):
        document=request.env[model_name].browse([document_id])
        document_sudo=document.with_user(SUPERUSER_ID).exists()
        ifnotdocument_sudo:
            raiseMissingError(_("Thisdocumentdoesnotexist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        exceptAccessError:
            ifnotaccess_tokenornotdocument_sudo.access_tokenornotconsteq(document_sudo.access_token,access_token):
                raise
        returndocument_sudo

    def_get_page_view_values(self,document,access_token,values,session_history,no_breadcrumbs,**kwargs):
        ifaccess_token:
            #ifno_breadcrumbs=False->forcebreadcrumbsevenifaccess_tokento`invite`userstoregisteriftheyclickonit
            values['no_breadcrumbs']=no_breadcrumbs
            values['access_token']=access_token
            values['token']=access_token #forportalchatter

        #Thoseareusednotablywheneverthepaymentformisimpliedintheportal.
        ifkwargs.get('error'):
            values['error']=kwargs['error']
        ifkwargs.get('warning'):
            values['warning']=kwargs['warning']
        ifkwargs.get('success'):
            values['success']=kwargs['success']
        #Emailtokenforpostingmessagesinportalviewwithidentifiedauthor
        ifkwargs.get('pid'):
            values['pid']=kwargs['pid']
        ifkwargs.get('hash'):
            values['hash']=kwargs['hash']

        history=request.session.get(session_history,[])
        values.update(get_records_pager(history,document))

        returnvalues

    def_show_report(self,model,report_type,report_ref,download=False):
        ifreport_typenotin('html','pdf','text'):
            raiseUserError(_("Invalidreporttype:%s",report_type))

        report_sudo=request.env.ref(report_ref).with_user(SUPERUSER_ID)

        ifnotisinstance(report_sudo,request.env.registry['ir.actions.report']):
            raiseUserError(_("%sisnotthereferenceofareport",report_ref))

        ifhasattr(model,'company_id'):
            report_sudo=report_sudo.with_company(model.company_id)

        method_name='_render_qweb_%s'%(report_type)
        report=getattr(report_sudo,method_name)([model.id],data={'report_type':report_type})[0]
        reporthttpheaders=[
            ('Content-Type','application/pdf'ifreport_type=='pdf'else'text/html'),
            ('Content-Length',len(report)),
        ]
        ifreport_type=='pdf'anddownload:
            filename="%s.pdf"%(re.sub('\W+','-',model._get_report_base_filename()))
            reporthttpheaders.append(('Content-Disposition',content_disposition(filename)))
        returnrequest.make_response(report,headers=reporthttpheaders)

defget_error(e,path=''):
    """Recursivelydereferences`path`(aperiod-separatedsequenceofdict
    keys)in`e`(anerrordictorvalue),returnsthefinalresolutionIIFit's
    anstr,otherwisereturnsNone
    """
    forkin(path.split('.')ifpathelse[]):
        ifnotisinstance(e,dict):
            returnNone
        e=e.get(k)

    returneifisinstance(e,str)elseNone
