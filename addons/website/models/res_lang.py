#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,tools,_
fromflectra.addons.website.modelsimportir_http
fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest


classLang(models.Model):
    _inherit="res.lang"

    defwrite(self,vals):
        if'active'invalsandnotvals['active']:
            ifself.env['website'].search([('language_ids','in',self._ids)]):
                raiseUserError(_("Cannotdeactivatealanguagethatiscurrentlyusedonawebsite."))
        returnsuper(Lang,self).write(vals)

    @api.model
    @tools.ormcache_context(keys=("website_id",))
    defget_available(self):
        website=ir_http.get_request_website()
        ifnotwebsite:
            returnsuper().get_available()
        #Returnthewebsite-availableonesinthiscase
        returnrequest.website.language_ids.get_sorted()
