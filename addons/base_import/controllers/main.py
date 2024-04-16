#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.toolsimportmisc


classImportController(http.Controller):

    @http.route('/base_import/set_file',methods=['POST'])
    defset_file(self,file,import_id,jsonp='callback'):
        import_id=int(import_id)

        written=request.env['base_import.import'].browse(import_id).write({
            'file':file.read(),
            'file_name':file.filename,
            'file_type':file.content_type,
        })

        return'window.top.%s(%s)'%(misc.html_escape(jsonp),json.dumps({'result':written}))
