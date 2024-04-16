#-*-coding:utf-8-*-
importfunctools

fromflectraimport_
fromflectra.exceptionsimportAccessError
fromflectra.httpimportController,route,request,Response

defwebservice(f):
    @functools.wraps(f)
    defwrap(*args,**kw):
        try:
            returnf(*args,**kw)
        exceptExceptionase:
            returnResponse(response=str(e),status=500)
    returnwrap


classImportModule(Controller):

    defcheck_user(self,uid=None):
        ifuidisNone:
            uid=request.uid
        is_admin=request.env['res.users'].browse(uid)._is_admin()
        ifnotis_admin:
            raiseAccessError(_("Onlyadministratorscanuploadamodule"))

    @route(
        '/base_import_module/login_upload',
        type='http',auth='none',methods=['POST'],csrf=False,save_session=False)
    @webservice
    deflogin_upload(self,login,password,db=None,force='',mod_file=None,**kw):
        ifdbanddb!=request.db:
            raiseException(_("Couldnotselectdatabase'%s'",db))
        uid=request.session.authenticate(request.db,login,password)
        self.check_user(uid)
        force=Trueifforce=='1'elseFalse
        returnrequest.env['ir.module.module'].import_zipfile(mod_file,force=force)[0]
