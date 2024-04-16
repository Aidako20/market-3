#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromrandomimportrandint

fromflectraimportfields,models


classTrackTag(models.Model):
    _name="event.track.tag"
    _description='EventTrackTag'
    _order="category_id,sequence,name"

    def_default_color(self):
        returnrandint(1,11)

    name=fields.Char('TagName',required=True)
    track_ids=fields.Many2many('event.track',string='Tracks')
    color=fields.Integer(
        string='ColorIndex',default=lambdaself:self._default_color(),
        help="Notethatcolorlesstagswon'tbeavailableonthewebsite.")
    sequence=fields.Integer('Sequence',default=10)
    category_id=fields.Many2one('event.track.tag.category',string="Category",ondelete="setnull")

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]
