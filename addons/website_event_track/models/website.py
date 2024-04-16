#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromPILimportImage

fromflectraimportapi,fields,models
fromflectra.exceptionsimportValidationError
fromflectra.toolsimportImageProcess
fromflectra.tools.translateimport_


classWebsite(models.Model):
    _inherit="website"

    app_icon=fields.Image(string='WebsiteAppIcon',compute='_compute_app_icon',store=True,readonly=True,help='Thisfieldholdstheimageusedasmobileappicononthewebsite(PNGformat).')
    events_app_name=fields.Char(string='EventsAppName',compute='_compute_events_app_name',store=True,readonly=False,help="ThisfieldsholdstheEvent'sProgressiveWebAppname.")

    @api.depends('name')
    def_compute_events_app_name(self):
        forwebsiteinself:
            ifnotwebsite.events_app_name:
                website.events_app_name=_('%sEvents')%website.name

    @api.constrains('events_app_name')
    def_check_events_app_name(self):
        forwebsiteinself:
            ifnotwebsite.events_app_name:
                raiseValidationError(_('"EventsAppName"fieldisrequired.'))

    @api.depends('favicon')
    def_compute_app_icon(self):
        """Computesasquaredimagebasedonthefavicontobeusedasmobilewebappicon.
            AppIconshouldbeinPNGformatandsizeofatleast512x512.

            IfthefaviconisanSVGimage,itwillbeskippedandtheapp_iconwillbesettoFalse.

        """
        forwebsiteinself:
            image=ImageProcess(website.favicon)ifwebsite.faviconelseNone
            ifnot(imageandimage.image):
                website.app_icon=False
                continue
            w,h=image.image.size
            square_size=wifw>helseh
            image.crop_resize(square_size,square_size)
            image.image=image.image.resize((512,512))
            image.operationsCount+=1
            website.app_icon=image.image_base64(output_format='PNG')
