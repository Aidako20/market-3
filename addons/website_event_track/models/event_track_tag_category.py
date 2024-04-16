#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classTrackTagCategory(models.Model):
    _name="event.track.tag.category"
    _description='EventTrackTagCategory'
    _order="sequence"

    name=fields.Char("Name",required=True,translate=True)
    sequence=fields.Integer('Sequence',default=10)
    tag_ids=fields.One2many('event.track.tag','category_id',string="Tags")
