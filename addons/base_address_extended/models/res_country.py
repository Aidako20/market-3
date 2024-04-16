#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResCountry(models.Model):
    _inherit='res.country'

    street_format=fields.Text(
        help="Formattouseforstreetsbelongingtothiscountry.\n\n"
             "Youcanusethepython-stylestringpatternwithallthefieldsofthestreet"
             "(forexample,use'%(street_name)s,%(street_number)s'ifyouwanttodisplay"
             "thestreetname,followedbyacommaandthehousenumber)"
             "\n%(street_name)s:thenameofthestreet"
             "\n%(street_number)s:thehousenumber"
             "\n%(street_number2)s:thedoornumber",
        default='%(street_number)s/%(street_number2)s%(street_name)s',required=True)

    @api.onchange("street_format")
    defonchange_street_format(self):
        #Preventunexpectedtruncationwithwhitespacesinfrontofthestreetformat
        self.street_format=self.street_format.strip()
