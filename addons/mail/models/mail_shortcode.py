#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMailShortcode(models.Model):
    """Shortcode
        CannedResponses,allowingtheusertodefinedshortcutsinitsmessage.Shouldbeappliedbeforestoringmessageindatabase.
        Emojiallowingreplacingtextwithimageforvisualeffect.Shouldbeappliedwhenthemessageisdisplayed(onlyforfinalrendering).
        Theseshortcodesareglobalandareavailableforeveryuser.
    """

    _name='mail.shortcode'
    _description='CannedResponse/Shortcode'
    source=fields.Char('Shortcut',required=True,index=True,help="TheshortcutwhichmustbereplacedintheChatMessages")
    substitution=fields.Text('Substitution',required=True,index=True,help="Theescapedhtmlcodereplacingtheshortcut")
    description=fields.Char('Description')
    message_ids=fields.Many2one('mail.message',string="Messages",store=False)
