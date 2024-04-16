#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importast

fromflectraimportapi,fields,models,_


classJob(models.Model):
    _name="hr.job"
    _inherit=["mail.alias.mixin","hr.job"]
    _order="statedesc,nameasc"

    @api.model
    def_default_address_id(self):
        returnself.env.company.partner_id

    def_get_default_favorite_user_ids(self):
        return[(6,0,[self.env.uid])]

    address_id=fields.Many2one(
        'res.partner',"JobLocation",default=_default_address_id,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",
        help="Addresswhereemployeesareworking")
    application_ids=fields.One2many('hr.applicant','job_id',"Applications")
    application_count=fields.Integer(compute='_compute_application_count',string="ApplicationCount")
    all_application_count=fields.Integer(compute='_compute_all_application_count',string="AllApplicationCount")
    new_application_count=fields.Integer(
        compute='_compute_new_application_count',string="NewApplication",
        help="Numberofapplicationsthatarenewintheflow(typicallyatfirststepoftheflow)")
    manager_id=fields.Many2one(
        'hr.employee',related='department_id.manager_id',string="DepartmentManager",
        readonly=True,store=True)
    user_id=fields.Many2one('res.users',"Recruiter",tracking=True)
    hr_responsible_id=fields.Many2one(
        'res.users',"HRResponsible",tracking=True,
        help="Personresponsibleofvalidatingtheemployee'scontracts.")
    document_ids=fields.One2many('ir.attachment',compute='_compute_document_ids',string="Documents")
    documents_count=fields.Integer(compute='_compute_document_ids',string="DocumentCount")
    alias_id=fields.Many2one(
        'mail.alias',"Alias",ondelete="restrict",required=True,
        help="Emailaliasforthisjobposition.Newemailswillautomaticallycreatenewapplicantsforthisjobposition.")
    color=fields.Integer("ColorIndex")
    is_favorite=fields.Boolean(compute='_compute_is_favorite',inverse='_inverse_is_favorite')
    favorite_user_ids=fields.Many2many('res.users','job_favorite_user_rel','job_id','user_id',default=_get_default_favorite_user_ids)

    def_compute_is_favorite(self):
        forjobinself:
            job.is_favorite=self.env.userinjob.favorite_user_ids

    def_inverse_is_favorite(self):
        unfavorited_jobs=favorited_jobs=self.env['hr.job']
        forjobinself:
            ifself.env.userinjob.favorite_user_ids:
                unfavorited_jobs|=job
            else:
                favorited_jobs|=job
        favorited_jobs.write({'favorite_user_ids':[(4,self.env.uid)]})
        unfavorited_jobs.write({'favorite_user_ids':[(3,self.env.uid)]})

    def_compute_document_ids(self):
        applicants=self.mapped('application_ids').filtered(lambdaself:notself.emp_id)
        app_to_job=dict((applicant.id,applicant.job_id.id)forapplicantinapplicants)
        attachments=self.env['ir.attachment'].search([
            '|',
            '&',('res_model','=','hr.job'),('res_id','in',self.ids),
            '&',('res_model','=','hr.applicant'),('res_id','in',applicants.ids)])
        result=dict.fromkeys(self.ids,self.env['ir.attachment'])
        forattachmentinattachments:
            ifattachment.res_model=='hr.applicant':
                result[app_to_job[attachment.res_id]]|=attachment
            else:
                result[attachment.res_id]|=attachment

        forjobinself:
            job.document_ids=result.get(job.id,False)
            job.documents_count=len(job.document_ids)

    def_compute_all_application_count(self):
        read_group_result=self.env['hr.applicant'].with_context(active_test=False).read_group([('job_id','in',self.ids)],['job_id'],['job_id'])
        result=dict((data['job_id'][0],data['job_id_count'])fordatainread_group_result)
        forjobinself:
            job.all_application_count=result.get(job.id,0)

    def_compute_application_count(self):
        read_group_result=self.env['hr.applicant'].read_group([('job_id','in',self.ids)],['job_id'],['job_id'])
        result=dict((data['job_id'][0],data['job_id_count'])fordatainread_group_result)
        forjobinself:
            job.application_count=result.get(job.id,0)

    def_get_first_stage(self):
        self.ensure_one()
        returnself.env['hr.recruitment.stage'].search([
            '|',
            ('job_ids','=',False),
            ('job_ids','=',self.id)],order='sequenceasc',limit=1)

    def_compute_new_application_count(self):
        self.env.cr.execute(
            """
                WITHjob_stageAS(
                    SELECTDISTINCTON(j.id)j.idASjob_id,s.idASstage_id,s.sequenceASsequence
                      FROMhr_jobj
                 LEFTJOINhr_job_hr_recruitment_stage_relrel
                        ONrel.hr_job_id=j.id
                      JOINhr_recruitment_stages
                        ONs.id=rel.hr_recruitment_stage_id
                        ORs.idNOTIN(
                                        SELECT"hr_recruitment_stage_id"
                                          FROM"hr_job_hr_recruitment_stage_rel"
                                         WHERE"hr_recruitment_stage_id"ISNOTNULL
                                        )
                     WHEREj.idin%s
                  ORDERBY1,3asc
                )
                SELECTs.job_id,COUNT(a.id)ASnew_applicant
                  FROMhr_applicanta
                  JOINjob_stages
                    ONs.job_id=a.job_id
                   ANDa.stage_id=s.stage_id
                   ANDa.activeISTRUE
              GROUPBYs.job_id
            """,[tuple(self.ids),]
        )

        new_applicant_count=dict(self.env.cr.fetchall())
        forjobinself:
            job.new_application_count=new_applicant_count.get(job.id,0)

    def_alias_get_creation_values(self):
        values=super(Job,self)._alias_get_creation_values()
        values['alias_model_id']=self.env['ir.model']._get('hr.applicant').id
        ifself.id:
            values['alias_defaults']=defaults=ast.literal_eval(self.alias_defaultsor"{}")
            defaults.update({
                'job_id':self.id,
                'department_id':self.department_id.id,
                'company_id':self.department_id.company_id.idifself.department_idelseself.company_id.id,
            })
        returnvalues

    @api.model
    defcreate(self,vals):
        vals['favorite_user_ids']=vals.get('favorite_user_ids',[])+[(4,self.env.uid)]
        new_job=super(Job,self).create(vals)
        utm_linkedin=self.env.ref("utm.utm_source_linkedin",raise_if_not_found=False)
        ifutm_linkedin:
            source_vals={
                'source_id':utm_linkedin.id,
                'job_id':new_job.id,
            }
            self.env['hr.recruitment.source'].create(source_vals)
        returnnew_job

    def_creation_subtype(self):
        returnself.env.ref('hr_recruitment.mt_job_new')

    defaction_get_attachment_tree_view(self):
        action=self.env["ir.actions.actions"]._for_xml_id("base.action_attachment")
        action['context']={
            'default_res_model':self._name,
            'default_res_id':self.ids[0]
        }
        action['search_view_id']=(self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id,)
        action['domain']=['|','&',('res_model','=','hr.job'),('res_id','in',self.ids),'&',('res_model','=','hr.applicant'),('res_id','in',self.mapped('application_ids').ids)]
        returnaction

    defclose_dialog(self):
        return{'type':'ir.actions.act_window_close'}

    defedit_dialog(self):
        form_view=self.env.ref('hr.view_hr_job_form')
        return{
            'name':_('Job'),
            'res_model':'hr.job',
            'res_id':self.id,
            'views':[(form_view.id,'form'),],
            'type':'ir.actions.act_window',
            'target':'inline'
        }
