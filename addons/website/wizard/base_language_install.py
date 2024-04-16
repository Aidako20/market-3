#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classBaseLanguageInstall(models.TransientModel):

    _inherit="base.language.install"

    website_ids=fields.Many2many('website',string='Websitestotranslate')

    @api.model
    defdefault_get(self,fields):
        defaults=super(BaseLanguageInstall,self).default_get(fields)
        website_id=self._context.get('params',{}).get('website_id')
        ifwebsite_id:
            if'website_ids'notindefaults:
                defaults['website_ids']=[]
            defaults['website_ids'].append(website_id)
        returndefaults

    deflang_install(self):
        action=super(BaseLanguageInstall,self).lang_install()
        lang=self.env['res.lang']._lang_get(self.lang)
        ifself.website_idsandlang:
            self.website_ids.write({'language_ids':[(4,lang.id)]})
        params=self._context.get('params',{})
        if'url_return'inparams:
            return{
                'url':params['url_return'].replace('[lang]',self.lang),
                'type':'ir.actions.act_url',
                'target':'self'
            }
        returnaction
