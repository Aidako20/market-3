#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models
fromflectra.tools.translateimporthtml_translate


classDigestTip(models.Model):
    _name='digest.tip'
    _description='DigestTips'
    _order='sequence'

    sequence=fields.Integer(
        'Sequence',default=1,
        help='Usedtodisplaydigesttipinemailtemplatebaseonorder')
    name=fields.Char('Name',translate=True)
    user_ids=fields.Many2many(
        'res.users',string='Recipients',
        help='Usershavingalreadyreceivedthistip')
    tip_description=fields.Html('Tipdescription',translate=html_translate)
    group_id=fields.Many2one(
        'res.groups',string='AuthorizedGroup',
        default=lambdaself:self.env.ref('base.group_user'))
