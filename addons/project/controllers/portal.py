#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportOrderedDict
fromoperatorimportitemgetter

fromflectraimporthttp,_
fromflectra.exceptionsimportAccessError,MissingError
fromflectra.httpimportrequest
fromflectra.addons.portal.controllers.portalimportCustomerPortal,pagerasportal_pager
fromflectra.toolsimportgroupbyasgroupbyelem

fromflectra.osv.expressionimportOR


classCustomerPortal(CustomerPortal):

    def_prepare_home_portal_values(self,counters):
        values=super()._prepare_home_portal_values(counters)
        if'project_count'incounters:
            values['project_count']=request.env['project.project'].search_count([])\
                ifrequest.env['project.project'].check_access_rights('read',raise_exception=False)else0
        if'task_count'incounters:
            values['task_count']=request.env['project.task'].search_count([])\
                ifrequest.env['project.task'].check_access_rights('read',raise_exception=False)else0
        returnvalues

    #------------------------------------------------------------
    #MyProject
    #------------------------------------------------------------
    def_project_get_page_view_values(self,project,access_token,**kwargs):
        values={
            'page_name':'project',
            'project':project,
        }
        returnself._get_page_view_values(project,access_token,values,'my_projects_history',False,**kwargs)

    @http.route(['/my/projects','/my/projects/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_projects(self,page=1,date_begin=None,date_end=None,sortby=None,**kw):
        values=self._prepare_portal_layout_values()
        Project=request.env['project.project']
        domain=[]

        searchbar_sortings={
            'date':{'label':_('Newest'),'order':'create_datedesc'},
            'name':{'label':_('Name'),'order':'name'},
        }
        ifnotsortby:
            sortby='date'
        order=searchbar_sortings[sortby]['order']

        ifdate_beginanddate_end:
            domain+=[('create_date','>',date_begin),('create_date','<=',date_end)]

        #projectscount
        project_count=Project.search_count(domain)
        #pager
        pager=portal_pager(
            url="/my/projects",
            url_args={'date_begin':date_begin,'date_end':date_end,'sortby':sortby},
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        #contentaccordingtopagerandarchiveselected
        projects=Project.search(domain,order=order,limit=self._items_per_page,offset=pager['offset'])
        request.session['my_projects_history']=projects.ids[:100]

        values.update({
            'date':date_begin,
            'date_end':date_end,
            'projects':projects,
            'page_name':'project',
            'default_url':'/my/projects',
            'pager':pager,
            'searchbar_sortings':searchbar_sortings,
            'sortby':sortby
        })
        returnrequest.render("project.portal_my_projects",values)

    @http.route(['/my/project/<int:project_id>'],type='http',auth="public",website=True)
    defportal_my_project(self,project_id=None,access_token=None,**kw):
        try:
            project_sudo=self._document_check_access('project.project',project_id,access_token)
        except(AccessError,MissingError):
            returnrequest.redirect('/my')

        values=self._project_get_page_view_values(project_sudo,access_token,**kw)
        returnrequest.render("project.portal_my_project",values)

    #------------------------------------------------------------
    #MyTask
    #------------------------------------------------------------
    def_task_get_page_view_values(self,task,access_token,**kwargs):
        values={
            'page_name':'task',
            'task':task,
            'user':request.env.user
        }
        returnself._get_page_view_values(task,access_token,values,'my_tasks_history',False,**kwargs)

    @http.route(['/my/tasks','/my/tasks/page/<int:page>'],type='http',auth="user",website=True)
    defportal_my_tasks(self,page=1,date_begin=None,date_end=None,sortby=None,filterby=None,search=None,search_in='content',groupby=None,**kw):
        values=self._prepare_portal_layout_values()
        searchbar_sortings={
            'date':{'label':_('Newest'),'order':'create_datedesc'},
            'name':{'label':_('Title'),'order':'name'},
            'stage':{'label':_('Stage'),'order':'stage_id,project_id'},
            'project':{'label':_('Project'),'order':'project_id,stage_id'},
            'update':{'label':_('LastStageUpdate'),'order':'date_last_stage_updatedesc'},
        }
        searchbar_filters={
            'all':{'label':_('All'),'domain':[]},
        }
        searchbar_inputs={
            'content':{'input':'content','label':_('Search<spanclass="nolabel">(inContent)</span>')},
            'message':{'input':'message','label':_('SearchinMessages')},
            'customer':{'input':'customer','label':_('SearchinCustomer')},
            'stage':{'input':'stage','label':_('SearchinStages')},
            'project':{'input':'project','label':_('SearchinProject')},
            'all':{'input':'all','label':_('SearchinAll')},
        }
        searchbar_groupby={
            'none':{'input':'none','label':_('None')},
            'project':{'input':'project','label':_('Project')},
            'stage':{'input':'stage','label':_('Stage')},
        }

        #extendsfilterbycriteriawithprojectthecustomerhasaccessto
        projects=request.env['project.project'].search([])
        forprojectinprojects:
            searchbar_filters.update({
                str(project.id):{'label':project.name,'domain':[('project_id','=',project.id)]}
            })

        #extendsfilterbycriteriawithproject(criterianameistheprojectid)
        #Note:portaluserscan'tviewprojectstheydon'tfollow
        project_groups=request.env['project.task'].read_group([('project_id','notin',projects.ids)],
                                                                ['project_id'],['project_id'])
        forgroupinproject_groups:
            proj_id=group['project_id'][0]ifgroup['project_id']elseFalse
            proj_name=group['project_id'][1]ifgroup['project_id']else_('Others')
            searchbar_filters.update({
                str(proj_id):{'label':proj_name,'domain':[('project_id','=',proj_id)]}
            })

        #defaultsortbyvalue
        ifnotsortby:
            sortby='date'
        order=searchbar_sortings[sortby]['order']

        #defaultfilterbyvalue
        ifnotfilterby:
            filterby='all'
        domain=searchbar_filters.get(filterby,searchbar_filters.get('all'))['domain']

        #defaultgroupbyvalue
        ifnotgroupby:
            groupby='project'

        ifdate_beginanddate_end:
            domain+=[('create_date','>',date_begin),('create_date','<=',date_end)]

        #search
        ifsearchandsearch_in:
            search_domain=[]
            ifsearch_inin('content','all'):
                search_domain=OR([search_domain,['|',('name','ilike',search),('description','ilike',search)]])
            ifsearch_inin('customer','all'):
                search_domain=OR([search_domain,[('partner_id','ilike',search)]])
            ifsearch_inin('message','all'):
                search_domain=OR([search_domain,[('message_ids.body','ilike',search)]])
            ifsearch_inin('stage','all'):
                search_domain=OR([search_domain,[('stage_id','ilike',search)]])
            ifsearch_inin('project','all'):
                search_domain=OR([search_domain,[('project_id','ilike',search)]])
            domain+=search_domain

        #taskcount
        task_count=request.env['project.task'].search_count(domain)
        #pager
        pager=portal_pager(
            url="/my/tasks",
            url_args={'date_begin':date_begin,'date_end':date_end,'sortby':sortby,'filterby':filterby,'groupby':groupby,'search_in':search_in,'search':search},
            total=task_count,
            page=page,
            step=self._items_per_page
        )
        #contentaccordingtopagerandarchiveselected
        ifgroupby=='project':
            order="project_id,%s"%order #forcesortonprojectfirsttogroupbyprojectinview
        elifgroupby=='stage':
            order="stage_id,%s"%order #forcesortonstagefirsttogroupbystageinview

        tasks=request.env['project.task'].search(domain,order=order,limit=self._items_per_page,offset=pager['offset'])
        request.session['my_tasks_history']=tasks.ids[:100]

        ifgroupby=='project':
            grouped_tasks=[request.env['project.task'].concat(*g)fork,gingroupbyelem(tasks,itemgetter('project_id'))]
        elifgroupby=='stage':
            grouped_tasks=[request.env['project.task'].concat(*g)fork,gingroupbyelem(tasks,itemgetter('stage_id'))]
        else:
            grouped_tasks=[tasks]iftaskselse[]

        values.update({
            'date':date_begin,
            'date_end':date_end,
            'grouped_tasks':grouped_tasks,
            'page_name':'task',
            'default_url':'/my/tasks',
            'pager':pager,
            'searchbar_sortings':searchbar_sortings,
            'searchbar_groupby':searchbar_groupby,
            'searchbar_inputs':searchbar_inputs,
            'search_in':search_in,
            'search':search,
            'sortby':sortby,
            'groupby':groupby,
            'searchbar_filters':OrderedDict(sorted(searchbar_filters.items())),
            'filterby':filterby,
        })
        returnrequest.render("project.portal_my_tasks",values)

    @http.route(['/my/task/<int:task_id>'],type='http',auth="public",website=True)
    defportal_my_task(self,task_id,access_token=None,**kw):
        try:
            task_sudo=self._document_check_access('project.task',task_id,access_token)
        except(AccessError,MissingError):
            returnrequest.redirect('/my')

        #ensureattachmentareaccessiblewithaccesstokeninsidetemplate
        forattachmentintask_sudo.attachment_ids:
            attachment.generate_access_token()
        values=self._task_get_page_view_values(task_sudo,access_token,**kw)
        returnrequest.render("project.portal_my_task",values)
