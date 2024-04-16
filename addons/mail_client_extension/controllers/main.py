#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importdatetime
importhmac
importjson
importlogging
importflectra
importrequests
importwerkzeug

importflectra.addons.iap.tools.iap_tools
fromflectraimporthttp,tools
fromflectra.httpimportrequest
fromflectra.tools.miscimportformatLang

_logger=logging.getLogger(__name__)

#Thetop100emailprovidersasI'mwritingthiscomment.
#Wedon'twanttoattemptmatchingcompaniesinthedatabasebasedonthosedomains,orwewillendupwithmultiple
#and/orthewrongcompany.Thissolutionwon'tworkallthetime,thegoalistocovermostcases.
_DOMAIN_BLACKLIST={'gmail.com','yahoo.com','hotmail.com','aol.com','hotmail.co.uk','hotmail.fr','msn.com',
                     'yahoo.fr','wanadoo.fr','orange.fr','comcast.net','yahoo.co.uk','yahoo.com.br','yahoo.co.in',
                     'live.com','rediffmail.com','free.fr','gmx.de','web.de','yandex.ru','ymail.com','libero.it',
                     'outlook.com','uol.com.br','bol.com.br','mail.ru','cox.net','hotmail.it','sbcglobal.net',
                     'sfr.fr','live.fr','verizon.net','live.co.uk','googlemail.com','yahoo.es','ig.com.br',
                     'live.nl','bigpond.com','terra.com.br','yahoo.it','neuf.fr','yahoo.de','alice.it',
                     'rocketmail.com','att.net','laposte.net','facebook.com','bellsouth.net','yahoo.in',
                     'hotmail.es','charter.net','yahoo.ca','yahoo.com.au','rambler.ru','hotmail.de','tiscali.it',
                     'shaw.ca','yahoo.co.jp','sky.com','earthlink.net','optonline.net','freenet.de','t-online.de',
                     'aliceadsl.fr','virgilio.it','home.nl','qq.com','telenet.be','me.com','yahoo.com.ar',
                     'tiscali.co.uk','yahoo.com.mx','voila.fr','gmx.net','mail.com','planet.nl','tin.it',
                     'live.it','ntlworld.com','arcor.de','yahoo.co.id','frontiernet.net','hetnet.nl',
                     'live.com.au','yahoo.com.sg','zonnet.nl','club-internet.fr','juno.com','optusnet.com.au',
                     'blueyonder.co.uk','bluewin.ch','skynet.be','sympatico.ca','windstream.net','mac.com',
                     'centurytel.net','chello.nl','live.ca','aim.com','bigpond.net.au'}


classMailClientExtensionController(http.Controller):

    @http.route('/mail_client_extension/auth',type='http',auth="user",methods=['GET'],website=True)
    defauth(self,**values):
        """
         OnceauthenticatedthisrouterenderstheviewthatshowsanappwantstoaccessFlectra.
         Theuserisinvitedtoallowordenytheapp.Theformpoststo`/mail_client_extension/auth/confirm`.
         """
        returnrequest.render('mail_client_extension.app_auth',values)

    @http.route('/mail_client_extension/auth/confirm',type='http',auth="user",methods=['POST'])
    defauth_confirm(self,scope,friendlyname,redirect,info=None,do=None,**kw):
        """
        Calledbythe`app_auth`template.IftheuserdecidedtoallowtheapptoaccessFlectra,atemporaryauthcode
        isgeneratedandheisredirectedto`redirect`withthiscodeintheURL.Itshouldredirecttotheapp,and
        theappshouldthenexchangethisauthcodeforanaccesstokenbycalling
        `/mail_client_extension/auth/access_token`.
        """
        parsed_redirect=werkzeug.urls.url_parse(redirect)
        params=parsed_redirect.decode_query()
        ifdo:
            name=friendlynameifnotinfoelsef'{friendlyname}:{info}'
            auth_code=self._generate_auth_code(scope,name)
            #paramsisaMultiDictwhichdoesnotsupport.update()withkwargs
            params.update({'success':1,'auth_code':auth_code})
        else:
            params['success']=0
        updated_redirect=parsed_redirect.replace(query=werkzeug.urls.url_encode(params))
        returnwerkzeug.utils.redirect(updated_redirect.to_url())

    #Inthiscase,anexceptionwillbethrownincaseofpreflightrequestifonlyPOSTisallowed.
    @http.route('/mail_client_extension/auth/access_token',type='json',auth="none",cors="*",methods=['POST','OPTIONS'])
    defauth_access_token(self,auth_code,**kw):
        """
        Calledbytheexternalapptoexchangeanauthcode,whichistemporaryandwaspassedinaURL,foran
        accesstoken,whichispermanent,andcanbeusedinthe`Authorization`headertoauthorizesubsequentrequests
        """
        auth_message=self._get_auth_code_data(auth_code)
        ifnotauth_message:
            return{"error":"Invalidcode"}
        request.uid=auth_message['uid']
        scope='flectra.plugin.'+auth_message.get('scope','')
        api_key=request.env['res.users.apikeys']._generate(scope,auth_message['name'])
        return{'access_token':api_key}

    def_get_auth_code_data(self,auth_code):
        data,auth_code_signature=auth_code.split('.')
        data=base64.b64decode(data)
        auth_code_signature=base64.b64decode(auth_code_signature)
        signature=flectra.tools.misc.hmac(request.env(su=True),'mail_client_extension',data).encode()
        ifnothmac.compare_digest(auth_code_signature,signature):
            returnNone

        auth_message=json.loads(data)
        #Checktheexpiration
        ifdatetime.datetime.utcnow()-datetime.datetime.fromtimestamp(auth_message['timestamp'])>datetime.timedelta(minutes=3):
            returnNone

        returnauth_message

    #UsingUTCexplicitlyincaseofadistributedsystemwherethegenerationandthesignatureverificationdonot
    #necessarilyhappenonthesameserver
    def_generate_auth_code(self,scope,name):
        auth_dict={
            'scope':scope,
            'name':name,
            'timestamp':int(datetime.datetime.utcnow().timestamp()), #<-elapsedtimeshouldbe<3minswhenverifying
            'uid':request.uid,
        }
        auth_message=json.dumps(auth_dict,sort_keys=True).encode()
        signature=flectra.tools.misc.hmac(request.env(su=True),'mail_client_extension',auth_message).encode()
        auth_code="%s.%s"%(base64.b64encode(auth_message).decode(),base64.b64encode(signature).decode())
        _logger.info('Authcodecreated-user%s,scope%s',request.env.user,scope)
        returnauth_code

    def_iap_enrich(self,domain):
        enriched_data={}
        try:
            response=request.env['iap.enrich.api']._request_enrich({domain:domain})#Thekeydoesn'tmatter
        #exceptflectra.addons.iap.models.iap.InsufficientCreditErrorasice:
        exceptflectra.addons.iap.tools.iap_tools.InsufficientCreditError:
            enriched_data['enrichment_info']={'type':'insufficient_credit','info':request.env['iap.account'].get_credits_url('reveal')}
        exceptExceptionase:
            enriched_data["enrichment_info"]={'type':'other','info':'Unknownreason'}
        else:
            enriched_data=response.get(domain)
            ifnotenriched_data:
                enriched_data={'enrichment_info':{'type':'no_data','info':'TheenrichmentAPIfoundnodatafortheemailprovided.'}}
        returnenriched_data

    @http.route('/mail_client_extension/modules/get',type="json",auth="outlook",csrf=False,cors="*")
    defmodules_get(self, **kwargs):
        return{'modules':['contacts','crm']}

    #Findanexistingcompanybasedontheemail.
    def_find_existing_company(self,domain):
        ifdomainin_DOMAIN_BLACKLIST:
            return
        returnrequest.env['res.partner'].search([('is_company','=',True),('email','=ilike','%'+domain)],limit=1)

    def_get_company_dict(self,company):
        ifnotcompany:
            return{'id':-1}

        return{
                    'id':company.id,
                    'name':company.name,
                    'phone':company.phone,
                    'mobile':company.mobile,
                    'email':company.email,
                    'address':{
                        'street':company.street,
                        'city':company.city,
                        'zip':company.zip,
                        'country':company.country_id.nameifcompany.country_idelse''
                    },
                    'website':company.website,
                    'additionalInfo':json.loads(company.iap_enrich_info)ifcompany.iap_enrich_infoelse{}
                }

    def_create_company_from_iap(self,domain):
        iap_data=self._iap_enrich(domain)
        if'enrichment_info'iniap_data:
            returnNone,iap_data['enrichment_info']

        phone_numbers=iap_data.get('phone_numbers')
        emails=iap_data.get('email')
        new_company_info={
            'is_company':True,
            'name':iap_data.get("name"),
            'street':iap_data.get("street_name"),
            'city':iap_data.get("city"),
            'zip':iap_data.get("postal_code"),
            'phone':phone_numbers[0]ifphone_numberselseNone,
            'website':iap_data.get("domain"),
            'email':emails[0]ifemailselseNone
        }

        logo_url=iap_data.get('logo')
        iflogo_url:
            try:
                response=requests.get(logo_url,timeout=2)
                ifresponse.ok:
                    new_company_info['image_1920']=base64.b64encode(response.content)
            exceptExceptionase:
                _logger.warning('Downloadofimagefornewcompany%rfailed,error%r'%(new_company_info.name,e))

        ifiap_data.get('country_code'):
            country=request.env['res.country'].search([('code','=',iap_data['country_code'].upper())])
            ifcountry:
                new_company_info['country_id']=country.id
                ifiap_data.get('state_code'):
                    state=request.env['res.country.state'].search([
                    ('code','=',iap_data['state_code']),
                    ('country_id','=',country.id)
                    ])
                    ifstate:
                        new_company_info['state_id']=state.id

        new_company_info['iap_enrich_info']=json.dumps(iap_data)
        new_company=request.env['res.partner'].create(new_company_info)
        new_company.message_post_with_view(
            'iap_mail.enrich_company',
            values=iap_data,
            subtype_id=request.env.ref('mail.mt_note').id,
        )
        
        returnnew_company,{'type':'company_created'}

    @http.route('/mail_client_extension/partner/get',type="json",auth="outlook",cors="*")
    defres_partner_get_by_email(self,email,name,**kwargs):
        response={}

        #computethesender'sdomain
        normalized_email=tools.email_normalize(email)
        ifnotnormalized_email:
            response['error']='Bademail.'
            returnresponse
        sender_domain=normalized_email.split('@')[1]

        #Searchforthepartnerbasedontheemail.
        #Ifmultiplearefound,takethefirstone.
        partner=request.env['res.partner'].search([('email','in',[normalized_email,email])],limit=1)
        ifpartner:
            response['partner']={
                'id':partner.id,
                'name':partner.name,
                'title':partner.function,
                'email':partner.email,
                'image':partner.image_128,
                'phone':partner.phone,
                'mobile':partner.mobile,
                'enrichment_info':None
            }
            #ifthereisalreadyacompanyforthispartner,justtakeitwithoutenrichment.
            ifpartner.parent_id:
                response['partner']['company']=self._get_company_dict(partner.parent_id)
            elifnotpartner.is_company:
                company=self._find_existing_company(sender_domain)
                ifnotcompany:#createandenrichcompany
                    company,enrichment_info=self._create_company_from_iap(sender_domain)
                    response['enrichment_info']=enrichment_info
                partner.write({'parent_id':company})
                response['partner']['company']=self._get_company_dict(company)
        else:#nopartnerfound
            response['partner']={
                'id':-1,
                'name':name,
                'email':email,
                'enrichment_info':None
            }
            company=self._find_existing_company(sender_domain)
            ifnotcompany: #createandenrichcompany
                company,enrichment_info=self._create_company_from_iap(sender_domain)
                response['enrichment_info']=enrichment_info
            response['partner']['company']=self._get_company_dict(company)

        returnresponse

    @http.route('/mail_client_extension/partner/create',type="json",auth="outlook",cors="*")
    defres_partner_create(self,email,name,company,**kwargs):
        #TODOsearchthecompanyagaininsteadofrelyingontheoneprovidedhere?
        #Createthepartnerifneeded.
        partner_info={
            'name':name,
            'email':email,
        }
        ifcompany>-1:
            partner_info['parent_id']=company
        partner=request.env['res.partner'].create(partner_info)

        response={'id':partner.id}
        returnresponse

    @http.route('/mail_client_extension/log_single_mail_content',type="json",auth="outlook",cors="*")
    deflog_single_mail_content(self,lead,message,**kw):
        crm_lead=request.env['crm.lead'].browse(lead)
        crm_lead.message_post(body=message)

    @http.route('/mail_client_extension/lead/get_by_partner_id',type="json",auth="outlook",cors="*")
    defcrm_lead_get_by_partner_id(self,partner,limit,offset,**kwargs):
        partner_leads=request.env['crm.lead'].search([('partner_id','=',partner)],offset=offset,limit=limit)
        leads=[]
        forleadinpartner_leads:
            leads.append({
                'id':lead.id,
                'name':lead.name,
                'expected_revenue':formatLang(request.env,lead.expected_revenue,monetary=True,currency_obj=lead.company_currency),
            })

        return{'leads':leads}

    @http.route('/mail_client_extension/lead/create_from_partner',type='http',auth='user',methods=['GET'])
    defcrm_lead_redirect_form_view(self,partner_id):
        server_action=http.request.env.ref("mail_client_extension.lead_creation_prefilled_action")
        returnwerkzeug.utils.redirect('/web#action=%s&model=crm.lead&partner_id=%s'%(server_action.id,int(partner_id)))
