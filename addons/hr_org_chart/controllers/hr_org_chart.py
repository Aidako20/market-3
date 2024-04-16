#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.exceptionsimportAccessError
fromflectra.httpimportrequest


classHrOrgChartController(http.Controller):
    _managers_level=5 #FPrequest

    def_check_employee(self,employee_id,**kw):
        ifnotemployee_id: #tocheck
            returnNone
        employee_id=int(employee_id)

        if'allowed_company_ids'inrequest.env.context:
            cids=request.env.context['allowed_company_ids']
        else:
            cids=[request.env.company.id]

        Employee=request.env['hr.employee.public'].with_context(allowed_company_ids=cids)
        #checkandraise
        ifnotEmployee.check_access_rights('read',raise_exception=False):
            returnNone
        try:
            Employee.browse(employee_id).check_access_rule('read')
        exceptAccessError:
            returnNone
        else:
            returnEmployee.browse(employee_id)

    def_prepare_employee_data(self,employee):
        job=employee.sudo().job_id
        returndict(
            id=employee.id,
            name=employee.name,
            link='/mail/view?model=%s&res_id=%s'%('hr.employee.public',employee.id,),
            job_id=job.id,
            job_name=job.nameor'',
            job_title=employee.job_titleor'',
            direct_sub_count=len(employee.child_ids-employee),
            indirect_sub_count=employee.child_all_count,
        )

    @http.route('/hr/get_redirect_model',type='json',auth='user')
    defget_redirect_model(self):
        ifrequest.env['hr.employee'].check_access_rights('read',raise_exception=False):
            return'hr.employee'
        return'hr.employee.public'

    @http.route('/hr/get_org_chart',type='json',auth='user')
    defget_org_chart(self,employee_id,**kw):

        employee=self._check_employee(employee_id,**kw)
        ifnotemployee: #tocheck
            return{
                'managers':[],
                'children':[],
            }

        #computeemployeedatafororgchart
        ancestors,current=request.env['hr.employee.public'].sudo(),employee.sudo()
        whilecurrent.parent_idandlen(ancestors)<self._managers_level+1andcurrent!=current.parent_id:
            ancestors+=current.parent_id
            current=current.parent_id

        values=dict(
            self=self._prepare_employee_data(employee),
            managers=[
                self._prepare_employee_data(ancestor)
                foridx,ancestorinenumerate(ancestors)
                ifidx<self._managers_level
            ],
            managers_more=len(ancestors)>self._managers_level,
            children=[self._prepare_employee_data(child)forchildinemployee.child_idsifchild!=employee],
        )
        values['managers'].reverse()
        returnvalues

    @http.route('/hr/get_subordinates',type='json',auth='user')
    defget_subordinates(self,employee_id,subordinates_type=None,**kw):
        """
        Getemployeesubordinates.
        Possiblevaluesfor'subordinates_type':
            -'indirect'
            -'direct'
        """
        employee=self._check_employee(employee_id,**kw)
        ifnotemployee: #tocheck
            return{}

        ifsubordinates_type=='direct':
            res=(employee.child_ids-employee).ids
        elifsubordinates_type=='indirect':
            res=(employee.subordinate_ids-employee.child_ids).ids
        else:
            res=employee.subordinate_ids.ids

        returnres
