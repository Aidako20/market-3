#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classTrackLocation(models.Model):
    _name="event.track.location"
    _description='EventTrackLocation'

    name=fields.Char('Location',required=True)
