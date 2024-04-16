#-*-coding:utf-8-*-
importwerkzeug
fromwerkzeug.exceptionsimportInternalServerError

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.web.controllers.mainimport_serialize_exception
fromflectra.tools.miscimporthtml_escape

importjson


classStockReportController(http.Controller):

    @http.route('/stock/<string:output_format>/<string:report_name>/<int:report_id>',type='http',auth='user')
    defreport(self,output_format,report_name,token,report_id=False,**kw):
        uid=request.session.uid
        domain=[('create_uid','=',uid)]
        stock_traceability=request.env['stock.traceability.report'].with_user(uid).search(domain,limit=1)
        line_data=json.loads(kw['data'])
        try:
            ifoutput_format=='pdf':
                response=request.make_response(
                    stock_traceability.with_context(active_id=report_id).get_pdf(line_data),
                    headers=[
                        ('Content-Type','application/pdf'),
                        ('Content-Disposition','attachment;filename='+'stock_traceability'+'.pdf;')
                    ]
                )
                response.set_cookie('fileToken',token)
                returnresponse
        exceptExceptionase:
            se=_serialize_exception(e)
            error={
                'code':200,
                'message':'FlectraServerError',
                'data':se
            }
            res=request.make_response(html_escape(json.dumps(error)))
            raiseInternalServerError(response=res)frome
