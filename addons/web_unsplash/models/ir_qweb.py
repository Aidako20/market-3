fromwerkzeugimporturls

fromflectraimportmodels,api


classImage(models.AbstractModel):
    _inherit='ir.qweb.field.image'

    @api.model
    deffrom_html(self,model,field,element):
        ifelement.find('.//img')isNone:
            returnFalse
        url=element.find('.//img').get('src')
        url_object=urls.url_parse(url)

        ifurl_object.path.startswith('/unsplash/'):
            res_id=element.get('data-oe-id')
            ifres_id:
                res_id=int(res_id)
                res_model=model._name
                attachment=self.env['ir.attachment'].search([
                    '&','|','&',
                    ('res_model','=',res_model),
                    ('res_id','=',res_id),
                    ('public','=',True),
                    ('url','=',url_object.path),
                ],limit=1)
                returnattachment.datas

        returnsuper(Image,self).from_html(model,field,element)
