#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
fromdateutil.relativedeltaimportrelativedelta
frompytzimportutc

fromflectraimportapi,fields,models


deftimezone_datetime(time):
    ifnottime.tzinfo:
        time=time.replace(tzinfo=utc)
    returntime


classResourceMixin(models.AbstractModel):
    _name="resource.mixin"
    _description='ResourceMixin'

    resource_id=fields.Many2one(
        'resource.resource','Resource',
        auto_join=True,index=True,ondelete='restrict',required=True)
    company_id=fields.Many2one(
        'res.company','Company',
        default=lambdaself:self.env.company,
        index=True,related='resource_id.company_id',store=True,readonly=False)
    resource_calendar_id=fields.Many2one(
        'resource.calendar','WorkingHours',
        default=lambdaself:self.env.company.resource_calendar_id,
        index=True,related='resource_id.calendar_id',store=True,readonly=False)
    tz=fields.Selection(
        string='Timezone',related='resource_id.tz',readonly=False,
        help="Thisfieldisusedinordertodefineinwhichtimezonetheresourceswillwork.")

    @api.model
    defcreate(self,values):
        ifnotvalues.get('resource_id'):
            resource_vals={'name':values.get(self._rec_name)}
            tz=(values.pop('tz',False)or
                  self.env['resource.calendar'].browse(values.get('resource_calendar_id')).tz)
            iftz:
                resource_vals['tz']=tz
            resource=self.env['resource.resource'].create(resource_vals)
            values['resource_id']=resource.id
        returnsuper(ResourceMixin,self).create(values)

    defcopy_data(self,default=None):
        ifdefaultisNone:
            default={}
        resource=self.resource_id.copy()
        default['resource_id']=resource.id
        default['company_id']=resource.company_id.id
        default['resource_calendar_id']=resource.calendar_id.id
        returnsuper(ResourceMixin,self).copy_data(default)

    #YTITODO:Removemeinmaster
    def_get_work_days_data(self,from_datetime,to_datetime,compute_leaves=True,calendar=None,domain=None):
        self.ensure_one()
        returnself._get_work_days_data_batch(
            from_datetime,
            to_datetime,
            compute_leaves=compute_leaves,
            calendar=calendar,
            domain=domain
        )[self.id]

    def_get_work_days_data_batch(self,from_datetime,to_datetime,compute_leaves=True,calendar=None,domain=None):
        """
            Bydefaulttheresourcecalendarisused,butitcanbe
            changedusingthe`calendar`argument.

            `domain`isusedinordertorecognisetheleavestotake,
            Nonemeansdefaultvalue('time_type','=','leave')

            Returnsadict{'days':n,'hours':h}containingthe
            quantityofworkingtimeexpressedasdaysandashours.
        """
        resources=self.mapped('resource_id')
        mapped_employees={e.resource_id.id:e.idforeinself}
        result={}

        #naivedatetimesaremadeexplicitinUTC
        from_datetime=timezone_datetime(from_datetime)
        to_datetime=timezone_datetime(to_datetime)

        mapped_resources=defaultdict(lambda:self.env['resource.resource'])
        forrecordinself:
            mapped_resources[calendarorrecord.resource_calendar_id]|=record.resource_id

        forcalendar,calendar_resourcesinmapped_resources.items():
            ifnotcalendar:
                forcalendar_resourceincalendar_resources:
                    result[calendar_resource.id]={'days':0,'hours':0}
                continue
            day_total=calendar._get_resources_day_total(from_datetime,to_datetime,calendar_resources)

            #actualhoursperday
            ifcompute_leaves:
                intervals=calendar._work_intervals_batch(from_datetime,to_datetime,calendar_resources,domain)
            else:
                intervals=calendar._attendance_intervals_batch(from_datetime,to_datetime,calendar_resources)

            forcalendar_resourceincalendar_resources:
                result[calendar_resource.id]=calendar._get_days_data(intervals[calendar_resource.id],day_total[calendar_resource.id])

        #convert"resource:result"into"employee:result"
        return{mapped_employees[r.id]:result[r.id]forrinresources}

    #YTITODO:Removemeinmaster
    def_get_leave_days_data(self,from_datetime,to_datetime,calendar=None,domain=None):
        self.ensure_one()
        returnself._get_leave_days_data_batch(
            from_datetime,
            to_datetime,
            calendar=calendar,
            domain=domain
        )[self.id]

    def_get_leave_days_data_batch(self,from_datetime,to_datetime,calendar=None,domain=None):
        """
            Bydefaulttheresourcecalendarisused,butitcanbe
            changedusingthe`calendar`argument.

            `domain`isusedinordertorecognisetheleavestotake,
            Nonemeansdefaultvalue('time_type','=','leave')

            Returnsadict{'days':n,'hours':h}containingthenumberofleaves
            expressedasdaysandashours.
        """
        resources=self.mapped('resource_id')
        mapped_employees={e.resource_id.id:e.idforeinself}
        result={}

        #naivedatetimesaremadeexplicitinUTC
        from_datetime=timezone_datetime(from_datetime)
        to_datetime=timezone_datetime(to_datetime)

        mapped_resources=defaultdict(lambda:self.env['resource.resource'])
        forrecordinself:
            mapped_resources[calendarorrecord.resource_calendar_id]|=record.resource_id

        forcalendar,calendar_resourcesinmapped_resources.items():
            day_total=calendar._get_resources_day_total(from_datetime,to_datetime,calendar_resources)

            #computeactualhoursperday
            attendances=calendar._attendance_intervals_batch(from_datetime,to_datetime,calendar_resources)
            leaves=calendar._leave_intervals_batch(from_datetime,to_datetime,calendar_resources,domain)

            forcalendar_resourceincalendar_resources:
                result[calendar_resource.id]=calendar._get_days_data(
                    attendances[calendar_resource.id]&leaves[calendar_resource.id],
                    day_total[calendar_resource.id]
                )

        #convert"resource:result"into"employee:result"
        return{mapped_employees[r.id]:result[r.id]forrinresources}

    def_adjust_to_calendar(self,start,end):
        resource_results=self.resource_id._adjust_to_calendar(start,end)
        #changedictkeysfromresourcestoassociatedrecords.
        return{
            record:resource_results[record.resource_id]
            forrecordinself
        }

    deflist_work_time_per_day(self,from_datetime,to_datetime,calendar=None,domain=None):
        """
            Bydefaulttheresourcecalendarisused,butitcanbe
            changedusingthe`calendar`argument.

            `domain`isusedinordertorecognisetheleavestotake,
            Nonemeansdefaultvalue('time_type','=','leave')

            Returnsalistoftuples(day,hours)foreachday
            containingatleastanattendance.
        """
        resource=self.resource_id
        calendar=calendarorself.resource_calendar_id

        #naivedatetimesaremadeexplicitinUTC
        ifnotfrom_datetime.tzinfo:
            from_datetime=from_datetime.replace(tzinfo=utc)
        ifnotto_datetime.tzinfo:
            to_datetime=to_datetime.replace(tzinfo=utc)

        intervals=calendar._work_intervals_batch(from_datetime,to_datetime,resource,domain)[resource.id]
        result=defaultdict(float)
        forstart,stop,metainintervals:
            result[start.date()]+=(stop-start).total_seconds()/3600
        returnsorted(result.items())

    deflist_leaves(self,from_datetime,to_datetime,calendar=None,domain=None):
        """
            Bydefaulttheresourcecalendarisused,butitcanbe
            changedusingthe`calendar`argument.

            `domain`isusedinordertorecognisetheleavestotake,
            Nonemeansdefaultvalue('time_type','=','leave')

            Returnsalistoftuples(day,hours,resource.calendar.leaves)
            foreachleaveinthecalendar.
        """
        resource=self.resource_id
        calendar=calendarorself.resource_calendar_id

        #naivedatetimesaremadeexplicitinUTC
        ifnotfrom_datetime.tzinfo:
            from_datetime=from_datetime.replace(tzinfo=utc)
        ifnotto_datetime.tzinfo:
            to_datetime=to_datetime.replace(tzinfo=utc)

        attendances=calendar._attendance_intervals_batch(from_datetime,to_datetime,resource)[resource.id]
        leaves=calendar._leave_intervals_batch(from_datetime,to_datetime,resource,domain)[resource.id]
        result=[]
        forstart,stop,leavein(leaves&attendances):
            hours=(stop-start).total_seconds()/3600
            result.append((start.date(),hours,leave))
        returnresult
