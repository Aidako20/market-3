#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classHttp(models.AbstractModel):
    _inherit='ir.http'

    defbinary_content(self,xmlid=None,model='ir.attachment',id=None,field='datas',
                       unique=False,filename=None,filename_field='name',download=False,
                       mimetype=None,default_mimetype='application/octet-stream',
                       access_token=None):
        obj=None
        ifxmlid:
            obj=self._xmlid_to_obj(self.env,xmlid)
            ifobjandobj._name!='slide.slide':
                obj=None
        elifidandmodel=='slide.slide':
            obj=self.env[model].browse(int(id))
        ifobj:
            obj.check_access_rights('read')
            obj.check_access_rule('read')
        returnsuper(Http,self).binary_content(
            xmlid=xmlid,model=model,id=id,field=field,unique=unique,filename=filename,
            filename_field=filename_field,download=download,mimetype=mimetype,
            default_mimetype=default_mimetype,access_token=access_token)
