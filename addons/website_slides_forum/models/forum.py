#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classForum(models.Model):
    _inherit='forum.forum'

    slide_channel_ids=fields.One2many('slide.channel','forum_id','Courses',help="Editthecourselinkedtothisforumonthecourseform.")
    slide_channel_id=fields.Many2one('slide.channel','Course',compute='_compute_slide_channel_id',store=True)
    visibility=fields.Selection(related='slide_channel_id.visibility',help="ForumlinkedtoaCourse,thevisibilityistheoneappliedonthecourse.")

    @api.depends('slide_channel_ids')
    def_compute_slide_channel_id(self):
        forforuminself:
            ifforum.slide_channel_ids:
                forum.slide_channel_id=forum.slide_channel_ids[0]
            else:
                forum.slide_channel_id=None
