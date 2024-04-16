#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromdatetimeimportdatetime

fromflectraimportmodels,fields,api
fromflectra.osv.expressionimportAND


classResourceCalendar(models.Model):
    _inherit='resource.calendar'

    deftransfer_leaves_to(self,other_calendar,resources=None,from_date=None):
        """
            Transfersomeresource.calendar.leavesfrom'self'toanothercalendar'other_calendar'.
            Transferedleaveslinkedto`resources`(orallif`resources`isNone)andstarting
            after'from_date'(ortodayifNone).
        """
        from_date=from_dateorfields.Datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        domain=[
            ('calendar_id','in',self.ids),
            ('date_from','>=',from_date),
        ]
        domain=AND([domain,[('resource_id','in',resources.ids)]])ifresourceselsedomain

        self.env['resource.calendar.leaves'].search(domain).write({
            'calendar_id':other_calendar.id,
        })

