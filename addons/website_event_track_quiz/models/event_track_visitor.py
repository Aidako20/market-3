#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classTrackVisitor(models.Model):
    _name='event.track.visitor'
    _inherit=['event.track.visitor']

    quiz_completed=fields.Boolean('Completed')
    quiz_points=fields.Integer("QuizPoints",default=0)
