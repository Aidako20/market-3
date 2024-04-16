#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMeetingType(models.Model):

    _name='calendar.event.type'
    _description='EventMeetingType'

    name=fields.Char('Name',required=True)

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]
