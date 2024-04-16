#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.portal.controllers.webimportHome
fromflectra.exceptionsimportUserError,ValidationError,AccessError,MissingError,AccessDenied


classWebsiteTest(Home):

    @http.route('/test_view',type='http',auth='public',website=True,sitemap=False)
    deftest_view(self,**kwargs):
        returnrequest.render('test_website.test_view')

    @http.route('/ignore_args/converteronly/<string:a>/',type='http',auth="public",website=True,sitemap=False)
    deftest_ignore_args_converter_only(self,a):
        returnrequest.make_response(json.dumps(dict(a=a,kw=None)))

    @http.route('/ignore_args/none',type='http',auth="public",website=True,sitemap=False)
    deftest_ignore_args_none(self):
        returnrequest.make_response(json.dumps(dict(a=None,kw=None)))

    @http.route('/ignore_args/a',type='http',auth="public",website=True,sitemap=False)
    deftest_ignore_args_a(self,a):
        returnrequest.make_response(json.dumps(dict(a=a,kw=None)))

    @http.route('/ignore_args/kw',type='http',auth="public",website=True,sitemap=False)
    deftest_ignore_args_kw(self,a,**kw):
        returnrequest.make_response(json.dumps(dict(a=a,kw=kw)))

    @http.route('/ignore_args/converter/<string:a>/',type='http',auth="public",website=True,sitemap=False)
    deftest_ignore_args_converter(self,a,b='youhou',**kw):
        returnrequest.make_response(json.dumps(dict(a=a,b=b,kw=kw)))

    @http.route('/ignore_args/converter/<string:a>/nokw',type='http',auth="public",website=True,sitemap=False)
    deftest_ignore_args_converter_nokw(self,a,b='youhou'):
        returnrequest.make_response(json.dumps(dict(a=a,b=b)))

    @http.route('/multi_company_website',type='http',auth="public",website=True,sitemap=False)
    deftest_company_context(self):
        returnrequest.make_response(json.dumps(request.context.get('allowed_company_ids')))

    @http.route('/test_lang_url/<model("res.country"):country>',type='http',auth='public',website=True,sitemap=False)
    deftest_lang_url(self,**kwargs):
        returnrequest.render('test_website.test_view')

    #TestSession

    @http.route('/test_get_dbname',type='json',auth='public',website=True,sitemap=False)
    deftest_get_dbname(self,**kwargs):
        returnrequest.env.cr.dbname

    #TestError

    @http.route('/test_error_view',type='http',auth='public',website=True,sitemap=False)
    deftest_error_view(self,**kwargs):
        returnrequest.render('test_website.test_error_view')

    @http.route('/test_user_error_http',type='http',auth='public',website=True,sitemap=False)
    deftest_user_error_http(self,**kwargs):
        raiseUserError("Thisisauserhttptest")

    @http.route('/test_user_error_json',type='json',auth='public',website=True,sitemap=False)
    deftest_user_error_json(self,**kwargs):
        raiseUserError("Thisisauserrpctest")

    @http.route('/test_validation_error_http',type='http',auth='public',website=True,sitemap=False)
    deftest_validation_error_http(self,**kwargs):
        raiseValidationError("Thisisavalidationhttptest")

    @http.route('/test_validation_error_json',type='json',auth='public',website=True,sitemap=False)
    deftest_validation_error_json(self,**kwargs):
        raiseValidationError("Thisisavalidationrpctest")

    @http.route('/test_access_error_json',type='json',auth='public',website=True,sitemap=False)
    deftest_access_error_json(self,**kwargs):
        raiseAccessError("Thisisanaccessrpctest")

    @http.route('/test_access_error_http',type='http',auth='public',website=True,sitemap=False)
    deftest_access_error_http(self,**kwargs):
        raiseAccessError("Thisisanaccesshttptest")

    @http.route('/test_missing_error_json',type='json',auth='public',website=True,sitemap=False)
    deftest_missing_error_json(self,**kwargs):
        raiseMissingError("Thisisamissingrpctest")

    @http.route('/test_missing_error_http',type='http',auth='public',website=True,sitemap=False)
    deftest_missing_error_http(self,**kwargs):
        raiseMissingError("Thisisamissinghttptest")

    @http.route('/test_internal_error_json',type='json',auth='public',website=True,sitemap=False)
    deftest_internal_error_json(self,**kwargs):
        raisewerkzeug.exceptions.InternalServerError()

    @http.route('/test_internal_error_http',type='http',auth='public',website=True,sitemap=False)
    deftest_internal_error_http(self,**kwargs):
        raisewerkzeug.exceptions.InternalServerError()

    @http.route('/test_access_denied_json',type='json',auth='public',website=True,sitemap=False)
    deftest_denied_error_json(self,**kwargs):
        raiseAccessDenied("Thisisanaccessdeniedrpctest")

    @http.route('/test_access_denied_http',type='http',auth='public',website=True,sitemap=False)
    deftest_denied_error_http(self,**kwargs):
        raiseAccessDenied("Thisisanaccessdeniedhttptest")

    @http.route(['/get'],type='http',auth="public",methods=['GET'],website=True,sitemap=False)
    defget_method(self,**kw):
        returnrequest.make_response('get')

    @http.route(['/post'],type='http',auth="public",methods=['POST'],website=True,sitemap=False)
    defpost_method(self,**kw):
        returnrequest.make_response('post')

    @http.route(['/get_post'],type='http',auth="public",methods=['GET','POST'],website=True,sitemap=False)
    defget_post_method(self,**kw):
        returnrequest.make_response('get_post')

    @http.route(['/get_post_nomultilang'],type='http',auth="public",methods=['GET','POST'],website=True,multilang=False,sitemap=False)
    defget_post_method_no_multilang(self,**kw):
        returnrequest.make_response('get_post_nomultilang')

    #TestPerfs

    @http.route(['/empty_controller_test'],type='http',auth='public',website=True,multilang=False,sitemap=False)
    defempty_controller_test(self,**kw):
        return'BasicControllerContent'

    #TestRedirects
    @http.route(['/test_website/country/<model("res.country"):country>'],type='http',auth="public",website=True,sitemap=False)
    deftest_model_converter_country(self,country,**kw):
        returnrequest.render('test_website.test_redirect_view',{'country':country})

    @http.route(['/test_website/200/<model("test.model"):rec>'],type='http',auth="public",website=True,sitemap=False)
    deftest_model_converter_seoname(self,rec,**kw):
        returnrequest.make_response('ok')

    @http.route(['/test_website/test_redirect_view_qs'],type='http',auth="public",website=True,sitemap=False)
    deftest_redirect_view_qs(self,**kw):
        returnrequest.render('test_website.test_redirect_view_qs')
