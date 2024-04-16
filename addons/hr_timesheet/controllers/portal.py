#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportOrderedDict
fromdateutil.relativedeltaimportrelativedelta
fromoperatorimportitemgetter

fromflectraimportfields,http,_
fromflectra.httpimportrequest
fromflectra.toolsimportdate_utils,groupbyasgroupbyelem
fromflectra.osv.expressionimportAND,OR

fromflectra.addons.portal.controllers.portalimportCustomerPortal,pagerasportal_pager


classTimesheetCustomerPortal(CustomerPortal):

    def_prepare_home_portal_values(self,counters):
        values=super()._prepare_home_portal_values(counters)
        if'timesheet_count'incounters:
            domain=request.env['account.analytic.line']._timesheet_get_portal_domain()
            values['timesheet_count']=request.env['account.analytic.line'].sudo().search_count(domain)
        returnvalues

    def_get_searchbar_inputs(self):
        return{
            'all':{'input':'all','label':_('SearchinAll')},
            'project':{'input':'project','label':_('SearchinProject')},
            'name':{'input':'name','label':_('SearchinDescription')},
            'employee':{'input':'employee','label':_('SearchinEmployee')},
            'task':{'input':'task','label':_('SearchinTask')}
        }

    def_get_searchbar_groupby(self):
        return{
            'none':{'input':'none','label':_('None')},
            'project':{'input':'project','label':_('Project')},
            'task':{'input':'task','label':_('Task')},
            'date':{'input':'date','label':_('Date')},
            'employee':{'input':'employee','label':_('Employee')}
        }

    def_get_search_domain(self,search_in,search):
        search_domain=[]
        ifsearch_inin('project','all'):
            search_domain=OR([search_domain,[('project_id','ilike',search)]])
        ifsearch_inin('name','all'):
            search_domain=OR([search_domain,[('name','ilike',search)]])
        ifsearch_inin('employee','all'):
            search_domain=OR([search_domain,[('employee_id','ilike',search)]])
        ifsearch_inin('task','all'):
            search_domain=OR([search_domain,[('task_id','ilike',search)]])
        returnsearch_domain

    def_get_groupby_mapping(self):
        return{
            'project':'project_id',
            'task':'task_id',
            'employee':'employee_id',
            'date':'date'
        }

    @http.route(['/my/timesheets','/my/timesheets/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_timesheets(self,page=1,sortby=None,filterby=None,search=None,search_in='all',groupby='none',**kw):
        Timesheet_sudo=request.env['account.analytic.line'].sudo()
        values=self._prepare_portal_layout_values()
        domain=request.env['account.analytic.line']._timesheet_get_portal_domain()
        _items_per_page=100

        searchbar_sortings={
            'date':{'label':_('Newest'),'order':'datedesc'},
            'name':{'label':_('Description'),'order':'name'},
        }

        searchbar_inputs=self._get_searchbar_inputs()

        searchbar_groupby=self._get_searchbar_groupby()

        today=fields.Date.today()
        quarter_start,quarter_end=date_utils.get_quarter(today)
        last_week=today+relativedelta(weeks=-1)
        last_month=today+relativedelta(months=-1)
        last_year=today+relativedelta(years=-1)

        searchbar_filters={
            'all':{'label':_('All'),'domain':[]},
            'today':{'label':_('Today'),'domain':[("date","=",today)]},
            'week':{'label':_('Thisweek'),'domain':[('date','>=',date_utils.start_of(today,"week")),('date','<=',date_utils.end_of(today,'week'))]},
            'month':{'label':_('Thismonth'),'domain':[('date','>=',date_utils.start_of(today,'month')),('date','<=',date_utils.end_of(today,'month'))]},
            'year':{'label':_('Thisyear'),'domain':[('date','>=',date_utils.start_of(today,'year')),('date','<=',date_utils.end_of(today,'year'))]},
            'quarter':{'label':_('ThisQuarter'),'domain':[('date','>=',quarter_start),('date','<=',quarter_end)]},
            'last_week':{'label':_('Lastweek'),'domain':[('date','>=',date_utils.start_of(last_week,"week")),('date','<=',date_utils.end_of(last_week,'week'))]},
            'last_month':{'label':_('Lastmonth'),'domain':[('date','>=',date_utils.start_of(last_month,'month')),('date','<=',date_utils.end_of(last_month,'month'))]},
            'last_year':{'label':_('Lastyear'),'domain':[('date','>=',date_utils.start_of(last_year,'year')),('date','<=',date_utils.end_of(last_year,'year'))]},
        }
        #defaultsortbyvalue
        ifnotsortby:
            sortby='date'
        order=searchbar_sortings[sortby]['order']
        #defaultfilterbyvalue
        ifnotfilterby:
            filterby='all'
        domain=AND([domain,searchbar_filters[filterby]['domain']])

        ifsearchandsearch_in:
            domain+=self._get_search_domain(search_in,search)

        timesheet_count=Timesheet_sudo.search_count(domain)
        #pager
        pager=portal_pager(
            url="/my/timesheets",
            url_args={'sortby':sortby,'search_in':search_in,'search':search,'filterby':filterby,'groupby':groupby},
            total=timesheet_count,
            page=page,
            step=_items_per_page
        )

        defget_timesheets():
            groupby_mapping=self._get_groupby_mapping()
            field=groupby_mapping.get(groupby,None)
            orderby='%s,%s'%(field,order)iffieldelseorder
            timesheets=Timesheet_sudo.search(domain,order=orderby,limit=_items_per_page,offset=pager['offset'])
            iffield:
                ifgroupby=='date':
                    raw_timesheets_group=Timesheet_sudo.read_group(
                        domain,["unit_amount:sum","ids:array_agg(id)"],["date:day"]
                    )
                    grouped_timesheets=[(Timesheet_sudo.browse(group["ids"]),group["unit_amount"])forgroupinraw_timesheets_group]

                else:
                    time_data=Timesheet_sudo.read_group(domain,[field,'unit_amount:sum'],[field])
                    mapped_time=dict([(m[field][0]ifm[field]elseFalse,m['unit_amount'])formintime_data])
                    grouped_timesheets=[(Timesheet_sudo.concat(*g),mapped_time[k.id])fork,gingroupbyelem(timesheets,itemgetter(field))]
                returntimesheets,grouped_timesheets

            grouped_timesheets=[(
                timesheets,
                sum(Timesheet_sudo.search(domain).mapped('unit_amount'))
            )]iftimesheetselse[]
            returntimesheets,grouped_timesheets

        timesheets,grouped_timesheets=get_timesheets()

        values.update({
            'timesheets':timesheets,
            'grouped_timesheets':grouped_timesheets,
            'page_name':'timesheet',
            'default_url':'/my/timesheets',
            'pager':pager,
            'searchbar_sortings':searchbar_sortings,
            'search_in':search_in,
            'search':search,
            'sortby':sortby,
            'groupby':groupby,
            'searchbar_inputs':searchbar_inputs,
            'searchbar_groupby':searchbar_groupby,
            'searchbar_filters':OrderedDict(sorted(searchbar_filters.items())),
            'filterby':filterby,
            'is_uom_day':request.env['account.analytic.line']._is_timesheet_encode_uom_day(),
        })
        returnrequest.render("hr_timesheet.portal_my_timesheets",values)
