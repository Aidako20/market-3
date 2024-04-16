#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classTrackStage(models.Model):
    _name='event.track.stage'
    _description='EventTrackStage'
    _order='sequence,id'

    name=fields.Char(string='StageName',required=True,translate=True)
    sequence=fields.Integer(string='Sequence',default=1)
    mail_template_id=fields.Many2one(
        'mail.template',string='EmailTemplate',
        domain=[('model','=','event.track')],
        help="Ifsetanemailwillbesenttothecustomerwhenthetrackreachesthisstep.")
    fold=fields.Boolean(
        string='FoldedinKanban',
        help='Thisstageisfoldedinthekanbanviewwhentherearenorecordsinthatstagetodisplay.')
    is_accepted=fields.Boolean(
        string='AcceptedStage',
        help='Acceptedtracksaredisplayedinagendaviewsbutnotaccessible.')
    is_done=fields.Boolean(
        string='DoneStage',
        help='Donetracksareautomaticallypublishedsothattheyareavailableinfrontend.')
    is_cancel=fields.Boolean(string='CanceledStage')
    is_done=fields.Boolean()
    color=fields.Integer(string='Color')
