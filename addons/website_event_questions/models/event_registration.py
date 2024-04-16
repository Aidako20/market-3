#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classEventRegistration(models.Model):
    """Storeanswersonattendees."""
    _inherit='event.registration'

    registration_answer_ids=fields.One2many('event.registration.answer','registration_id',string='AttendeeAnswers')

classEventRegistrationAnswer(models.Model):
    """Representstheuserinputanswerforasingleevent.question"""
    _name='event.registration.answer'
    _description='EventRegistrationAnswer'

    question_id=fields.Many2one(
        'event.question',ondelete='restrict',required=True,
        domain="[('event_id','=',event_id)]")
    registration_id=fields.Many2one('event.registration',required=True,ondelete='cascade')
    partner_id=fields.Many2one('res.partner',related='registration_id.partner_id')
    event_id=fields.Many2one('event.event',related='registration_id.event_id')
    question_type=fields.Selection(related='question_id.question_type')
    value_answer_id=fields.Many2one('event.question.answer',string="Suggestedanswer")
    value_text_box=fields.Text('Textanswer')

    _sql_constraints=[
        ('value_check',"CHECK(value_answer_idISNOTNULLORCOALESCE(value_text_box,'')<>'')","Theremustbeasuggestedvalueoratextvalue.")
    ]
