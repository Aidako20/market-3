#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importcalendar

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models


classKarmaTracking(models.Model):
    _name='gamification.karma.tracking'
    _description='TrackKarmaChanges'
    _rec_name='user_id'
    _order='tracking_dateDESC'

    user_id=fields.Many2one('res.users','User',index=True,readonly=True,required=True,ondelete='cascade')
    old_value=fields.Integer('OldKarmaValue',required=True,readonly=True)
    new_value=fields.Integer('NewKarmaValue',required=True,readonly=True)
    consolidated=fields.Boolean('Consolidated')
    tracking_date=fields.Date(default=fields.Date.context_today)

    @api.model
    def_consolidate_last_month(self):
        """Consolidatelastmonth.Usedbyacrontocleanuptrackingrecords."""
        previous_month_start=fields.Date.today()+relativedelta(months=-1,day=1)
        returnself._process_consolidate(previous_month_start)

    def_process_consolidate(self,from_date):
        """Consolidatetrackingsintoasinglerecordforagivenmonth,starting
        atafrom_date(included).Enddateissettolastdayofcurrentmonth
        usingasmartcalendar.monthrangeconstruction."""
        end_date=from_date+relativedelta(day=calendar.monthrange(from_date.year,from_date.month)[1])
        select_query="""
SELECTuser_id,
(
    SELECTold_valuefromgamification_karma_trackingold_tracking
    WHEREold_tracking.user_id=gamification_karma_tracking.user_id
        ANDtracking_date::timestampBETWEEN%(from_date)sAND%(to_date)s
        ANDconsolidatedISNOTTRUE
        ORDERBYtracking_dateASCLIMIT1
),(
    SELECTnew_valuefromgamification_karma_trackingnew_tracking
    WHEREnew_tracking.user_id=gamification_karma_tracking.user_id
        ANDtracking_date::timestampBETWEEN%(from_date)sAND%(to_date)s
        ANDconsolidatedISNOTTRUE
        ORDERBYtracking_dateDESCLIMIT1
)
FROMgamification_karma_tracking
WHEREtracking_date::timestampBETWEEN%(from_date)sAND%(to_date)s
ANDconsolidatedISNOTTRUE
GROUPBYuser_id"""
        self.env.cr.execute(select_query,{
            'from_date':from_date,
            'to_date':end_date,
        })
        results=self.env.cr.dictfetchall()
        ifresults:
            forresultinresults:
                result['consolidated']=True
                result['tracking_date']=fields.Date.to_string(from_date)
            self.create(results)

            self.search([
                ('tracking_date','>=',from_date),
                ('tracking_date','<=',end_date),
                ('consolidated','!=',True)]
            ).unlink()
        returnTrue
