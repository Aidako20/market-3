#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importjson
importlogging

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.tools.translateimport_

logger=logging.getLogger(__name__)


classMrpDocumentRoute(http.Controller):

    @http.route('/mrp/upload_attachment',type='http',methods=['POST'],auth="user")
    defupload_document(self,ufile,**kwargs):
        files=request.httprequest.files.getlist('ufile')
        result={'success':_("Allfilesuploaded")}
        forufileinfiles:
            try:
                mimetype=ufile.content_type
                request.env['mrp.document'].create({
                    'name':ufile.filename,
                    'res_model':kwargs.get('res_model'),
                    'res_id':int(kwargs.get('res_id')),
                    'mimetype':mimetype,
                    'datas':base64.encodebytes(ufile.read()),
                })
            exceptExceptionase:
                logger.exception("Failtouploaddocument%s"%ufile.filename)
                result={'error':str(e)}

        returnjson.dumps(result)
