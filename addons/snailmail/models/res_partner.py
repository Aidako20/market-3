
#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models
fromflectra.addons.snailmail.country_utilsimportSNAILMAIL_COUNTRIES


classResPartner(models.Model):
    _inherit="res.partner"

    defwrite(self,vals):
        letter_address_vals={}
        address_fields=['street','street2','city','zip','state_id','country_id']
        forfieldinaddress_fields:
            iffieldinvals:
                letter_address_vals[field]=vals[field]

        ifletter_address_vals:
            letters=self.env['snailmail.letter'].search([
                ('state','notin',['sent','canceled']),
                ('partner_id','in',self.ids),
            ])
            letters.write(letter_address_vals)

        returnsuper(ResPartner,self).write(vals)

    def_get_country_name(self):
        #whensendingaletter,thusrenderingthereportwiththesnailmail_layout,
        #weneedtooverridethecountrynametoitsenglishversionfollowingthe
        #dictionaryimportedincountry_utils.py
        country_code=self.country_id.code
        ifself.env.context.get('snailmail_layout')andcountry_codeinSNAILMAIL_COUNTRIES:
            returnSNAILMAIL_COUNTRIES.get(country_code)

        returnsuper(ResPartner,self)._get_country_name()

    @api.model
    def_get_address_format(self):
        #Whensendingaletter,thefields'street'and'street2'shouldbeonasinglelinetofitintheaddressarea
        ifself.env.context.get('snailmail_layout')andself.street2:
            return"%(street)s,%(street2)s\n%(city)s%(state_code)s%(zip)s\n%(country_name)s"

        returnsuper(ResPartner,self)._get_address_format()
