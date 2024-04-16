#-*-coding:utf-8-*-
fromflectraimportmodels
fromflectra.httpimportrequest

classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    defsession_info(self):
        info=super().session_info()
        #becausefrontendsession_infousesthiskeyandisembeddedin
        #theviewsource
        info["user_id"]=request.session.uid,
        returninfo
