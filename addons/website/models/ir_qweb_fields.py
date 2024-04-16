#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_


classContact(models.AbstractModel):
    _inherit='ir.qweb.field.contact'

    @api.model
    defget_available_options(self):
        options=super(Contact,self).get_available_options()
        options.update(
            website_description=dict(type='boolean',string=_('Displaythewebsitedescription')),
            UserBio=dict(type='boolean',string=_('Displaythebiography')),
            badges=dict(type='boolean',string=_('Displaythebadges'))
        )
        returnoptions
