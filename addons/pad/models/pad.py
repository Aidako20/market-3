#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importrandom
importre
importstring

importrequests

fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError

from..py_etherpadimportEtherpadLiteClient

_logger=logging.getLogger(__name__)


classPadCommon(models.AbstractModel):
    _name='pad.common'
    _description='PadCommon'

    def_valid_field_parameter(self,field,name):
        returnname=='pad_content_field'orsuper()._valid_field_parameter(field,name)

    @api.model
    defpad_is_configured(self):
        returnbool(self.env.company.pad_server)

    @api.model
    defpad_generate_url(self):
        company=self.env.company.sudo()

        pad={
            "server":company.pad_server,
            "key":company.pad_key,
        }

        #makesurepadserverintheformofhttp://hostname
        ifnotpad["server"]:
            returnpad
        ifnotpad["server"].startswith('http'):
            pad["server"]='http://'+pad["server"]
        pad["server"]=pad["server"].rstrip('/')
        #generateasalt
        s=string.ascii_uppercase+string.digits
        salt=''.join([s[random.SystemRandom().randint(0,len(s)-1)]foriinrange(10)])
        #path
        #etherpadhardcodespadidlengthlimitto50
        path='-%s-%s'%(self._name,salt)
        path='%s%s'%(self.env.cr.dbname.replace('_','-')[0:50-len(path)],path)
        #contructtheurl
        url='%s/p/%s'%(pad["server"],path)

        #ifcreatewithcontent
        ifself.env.context.get('field_name')andself.env.context.get('model'):
            myPad=EtherpadLiteClient(pad["key"],pad["server"]+'/api')
            try:
                myPad.createPad(path)
            exceptIOError:
                raiseUserError(_("Padcreationfailed,eitherthereisaproblemwithyourpadserverURLorwithyourconnection."))

            #getattronthefieldmodel
            model=self.env[self.env.context["model"]]
            field=model._fields[self.env.context['field_name']]
            real_field=field.pad_content_field

            res_id=self.env.context.get("object_id")
            record=model.browse(res_id)
            #getcontentoftherealfield
            real_field_value=record[real_field]orself.env.context.get('record',{}).get(real_field,'')
            ifreal_field_value:
                myPad.setHtmlFallbackText(path,real_field_value)

        return{
            "server":pad["server"],
            "path":path,
            "url":url,
        }

    @api.model
    defpad_get_content(self,url):
        company=self.env.company.sudo()
        myPad=EtherpadLiteClient(company.pad_key,(company.pad_serveror'')+'/api')
        content=''
        ifurl:
            split_url=url.split('/p/')
            path=len(split_url)==2andsplit_url[1]
            try:
                content=myPad.getHtml(path).get('html','')
            exceptIOError:
                _logger.warning('HttpError:thecredentialsmightbeabsentforurl:"%s".Fallingback.'%url)
                try:
                    r=requests.get('%s/export/html'%url)
                    r.raise_for_status()
                exceptException:
                    _logger.warning("Nopadfoundwithurl'%s'.",url)
                else:
                    mo=re.search('<body>(.*)</body>',r.content.decode(),re.DOTALL)
                    ifmo:
                        content=mo.group(1)

        returncontent

    #TODO
    #reverseengineerprotocoltobesetHtmlwithoutusingtheapikey

    defwrite(self,vals):
        self._set_field_to_pad(vals)
        self._set_pad_to_field(vals)
        returnsuper(PadCommon,self).write(vals)

    @api.model
    defcreate(self,vals):
        #Caseofaregularcreation:wereceivethepadurl,soweneedtoupdatethe
        #correspondingfield
        self._set_pad_to_field(vals)
        pad=super(PadCommon,self).create(vals)

        #Caseofaprogrammaticalcreation(e.g.copy):wereceivethefieldcontent,soweneed
        #tocreatethecorrespondingpad
        ifself.env.context.get('pad_no_create',False):
            returnpad
        fork,fieldinself._fields.items():
            ifhasattr(field,'pad_content_field')andknotinvals:
                ctx={
                    'model':self._name,
                    'field_name':k,
                    'object_id':pad.id,
                }
                pad_info=self.with_context(**ctx).pad_generate_url()
                pad[k]=pad_info.get('url')
        returnpad

    def_set_field_to_pad(self,vals):
        #Updatethepadifthe`pad_content_field`ismodified
        fork,fieldinself._fields.items():
            ifhasattr(field,'pad_content_field')andvals.get(field.pad_content_field)andself[k]:
                company=self.env.user.sudo().company_id
                myPad=EtherpadLiteClient(company.pad_key,(company.pad_serveror'')+'/api')
                path=self[k].split('/p/')[1]
                myPad.setHtmlFallbackText(path,vals[field.pad_content_field])

    def_set_pad_to_field(self,vals):
        #Updatethe`pad_content_field`ifthepadismodified
        fork,vinlist(vals.items()):
            field=self._fields.get(k)
            ifhasattr(field,'pad_content_field'):
                vals[field.pad_content_field]=self.pad_get_content(v)
