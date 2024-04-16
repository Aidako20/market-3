#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromrandomimportrandint

fromflectraimportapi,fields,models


classEventTagCategory(models.Model):
    _name="event.tag.category"
    _description="EventTagCategory"
    _order="sequence"

    name=fields.Char("Name",required=True,translate=True)
    sequence=fields.Integer('Sequence',default=0)
    tag_ids=fields.One2many('event.tag','category_id',string="Tags")

classEventTag(models.Model):
    _name="event.tag"
    _description="EventTag"
    _order="sequence"

    def_default_color(self):
        returnrandint(1,11)

    name=fields.Char("Name",required=True,translate=True)
    sequence=fields.Integer('Sequence',default=0)
    category_id=fields.Many2one("event.tag.category",string="Category",required=True,ondelete='cascade')
    color=fields.Integer(
        string='ColorIndex',default=lambdaself:self._default_color(),
        help='Tagcolor.Nocolormeansnodisplayinkanbanorfront-end,todistinguishinternaltagsfrompubliccategorizationtags.')

    defname_get(self):
        return[(tag.id,"%s:%s"%(tag.category_id.name,tag.name))fortaginself]
