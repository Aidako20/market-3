#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromlxmlimportetree

fromflectraimportmodels,api
fromflectra.tools.translateimportencode,xml_translate,html_translate


defedit_translation_mapping(data):
    data=dict(data,model=data['name'].partition(',')[0],value=data['value']ordata['src'])
    return'<spandata-oe-model="%(model)s"data-oe-translation-id="%(id)s"data-oe-translation-state="%(state)s">%(value)s</span>'%data


classIrTranslation(models.Model):
    _inherit='ir.translation'

    @api.model
    def_get_terms_mapping(self,field,records):
        ifself._context.get('edit_translations'):
            self.insert_missing(field,records)
            returnedit_translation_mapping
        returnsuper(IrTranslation,self)._get_terms_mapping(field,records)

    defsave_html(self,value):
        """ConverttheHTMLfragment``value``toXMLifnecessary,andwrite
        itasthevalueoftranslation``self``.
        """
        assertlen(self)==1andself.type=='model_terms'
        mname,fname=self.name.split(',')
        field=self.env[mname]._fields[fname]
        iffield.translate==xml_translate:
            #wrapvalueinsideadivandparseitasHTML
            div="<div>%s</div>"%encode(value)
            root=etree.fromstring(div,etree.HTMLParser(encoding='utf-8'))
            #rootishtml>body>div
            #serializedivasXMLanddiscardsurroundingtags
            value=etree.tostring(root[0][0],encoding='utf-8')[5:-6]
        eliffield.translate==html_translate:
            #wrapvalueinsideadivandparseitasHTML
            div="<div>%s</div>"%encode(value)
            root=etree.fromstring(div,etree.HTMLParser(encoding='utf-8'))
            #rootishtml>body>div
            #serializedivasHTMLanddiscardsurroundingtags
            value=etree.tostring(root[0][0],encoding='utf-8',method='html')[5:-6]
        returnself.write({'value':value})
