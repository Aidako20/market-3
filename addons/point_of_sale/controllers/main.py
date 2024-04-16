#-*-coding:utf-8-*-
importjson
importlogging
importwerkzeug.utils

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.osv.expressionimportAND
fromflectra.toolsimportconvert

_logger=logging.getLogger(__name__)


classPosController(http.Controller):

    @http.route(['/pos/web','/pos/ui'],type='http',auth='user')
    defpos_web(self,config_id=False,**k):
        """Openapossessionforthegivenconfig.

        Therightpossessionwillbeselectedtoopen,ifnonisopenyetanewsessionwillbecreated.

        /pos/uiand/pos/webbothcanbeusedtoaccesthePOS.OntheSaaS,
        /pos/uiusesHTTPSwhile/pos/webusesHTTP.

        :paramdebug:Thedebugmodetoloadthesessionin.
        :typedebug:str.
        :paramconfig_id:idoftheconfigthathastobeloaded.
        :typeconfig_id:str.
        :returns:object--Therenderedpossession.
        """
        domain=[
                ('state','in',['opening_control','opened']),
                ('user_id','=',request.session.uid),
                ('rescue','=',False)
                ]
        ifconfig_id:
            domain=AND([domain,[('config_id','=',int(config_id))]])
        pos_session=request.env['pos.session'].sudo().search(domain,limit=1)

        #ThesamePOSsessioncanbeopenedbyadifferentuser=>searchwithoutrestrictingto
        #currentuser.Note:theconfigmustbeexplicitlygiventoavoidfallbackingonarandom
        #session.
        ifnotpos_sessionandconfig_id:
            domain=[
                ('state','in',['opening_control','opened']),
                ('rescue','=',False),
                ('config_id','=',int(config_id)),
            ]
            pos_session=request.env['pos.session'].sudo().search(domain,limit=1)

        ifnotpos_session:
            returnwerkzeug.utils.redirect('/web#action=point_of_sale.action_client_pos_menu')
        #ThePOSonlyworkinonecompany,soweenforcetheoneofthesessioninthecontext
        company=pos_session.company_id
        session_info=request.env['ir.http'].session_info()
        session_info['user_context']['allowed_company_ids']=company.ids
        session_info['user_companies']={'current_company':(company.id,company.name),'allowed_companies':[(company.id,company.name)]}
        context={
            'session_info':session_info,
            'login_number':pos_session.login(),
        }
        response=request.render('point_of_sale.index',context)
        response.headers['Cache-Control']='no-store'
        returnresponse

    @http.route('/pos/ui/tests',type='http',auth="user")
    deftest_suite(self,mod=None,**kwargs):
        domain=[
            ('state','=','opened'),
            ('user_id','=',request.session.uid),
            ('rescue','=',False)
        ]
        pos_session=request.env['pos.session'].sudo().search(domain,limit=1)
        session_info=request.env['ir.http'].session_info()
        session_info['user_context']['allowed_company_ids']=pos_session.company_id.ids
        context={
            'session_info':session_info,
        }
        returnrequest.render('point_of_sale.qunit_suite',qcontext=context)

    @http.route('/pos/sale_details_report',type='http',auth='user')
    defprint_sale_details(self,date_start=False,date_stop=False,**kw):
        r=request.env['report.point_of_sale.report_saledetails']
        pdf,_=request.env.ref('point_of_sale.sale_details_report').with_context(date_start=date_start,date_stop=date_stop)._render_qweb_pdf(r)
        pdfhttpheaders=[('Content-Type','application/pdf'),('Content-Length',len(pdf))]
        returnrequest.make_response(pdf,headers=pdfhttpheaders)

    @http.route('/pos/load_onboarding_data',type='json',auth='user')
    defload_onboarding_data(self):
        convert.convert_file(request.env.cr,'point_of_sale','data/point_of_sale_onboarding.xml',None,mode='init',kind='data')
