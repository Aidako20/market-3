#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.httpimportrequest
fromwerkzeug.exceptionsimportNotFound


classWebsiteHrRecruitment(http.Controller):
    defsitemap_jobs(env,rule,qs):
        ifnotqsorqs.lower()in'/jobs':
            yield{'loc':'/jobs'}

    @http.route([
        '/jobs',
        '/jobs/country/<model("res.country"):country>',
        '/jobs/department/<model("hr.department"):department>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
        '/jobs/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
        '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
    ],type='http',auth="public",website=True,sitemap=sitemap_jobs)
    defjobs(self,country=None,department=None,office_id=None,**kwargs):
        env=request.env(context=dict(request.env.context,show_address=True,no_tag_br=True))

        Country=env['res.country']
        Jobs=env['hr.job']

        #ListjobsavailabletocurrentUID
        domain=request.website.website_domain()
        job_ids=Jobs.search(domain,order="is_publisheddesc,no_of_recruitmentdesc").ids
        #Browsejobsassuperuser,becauseaddressisrestricted
        jobs=Jobs.sudo().browse(job_ids)

        #Defaultsearchbyusercountry
        ifnot(countryordepartmentoroffice_idorkwargs.get('all_countries')):
            country_code=request.session['geoip'].get('country_code')
            ifcountry_code:
                countries_=Country.search([('code','=',country_code)])
                country=countries_[0]ifcountries_elseNone
                ifnotany(jforjinjobsifj.address_idandj.address_id.country_id==country):
                    country=False

        #Filterjob/officeforcountry
        ifcountryandnotkwargs.get('all_countries'):
            jobs=[jforjinjobsifnotj.address_idorj.address_id.country_id.id==country.id]
            offices=set(j.address_idforjinjobsifnotj.address_idorj.address_id.country_id.id==country.id)
        else:
            offices=set(j.address_idforjinjobsifj.address_id)

        #Deducedepartmentsandcountriesofficesofthosejobs
        departments=set(j.department_idforjinjobsifj.department_id)
        countries=set(o.country_idforoinofficesifo.country_id)

        ifdepartment:
            jobs=[jforjinjobsifj.department_idandj.department_id.id==department.id]
        ifoffice_idandoffice_idin[x.idforxinoffices]:
            jobs=[jforjinjobsifj.address_idandj.address_id.id==office_id]
        else:
            office_id=False

        #Renderpage
        returnrequest.render("website_hr_recruitment.index",{
            'jobs':jobs,
            'countries':countries,
            'departments':departments,
            'offices':offices,
            'country_id':country,
            'department_id':department,
            'office_id':office_id,
        })

    @http.route('/jobs/add',type='http',auth="user",website=True)
    defjobs_add(self,**kwargs):
        #avoidbrandingofwebsite_descriptionbysettingrendering_bundleincontext
        job=request.env['hr.job'].with_context(rendering_bundle=True).create({
            'name':_('JobTitle'),
        })
        returnrequest.redirect("/jobs/detail/%s?enable_editor=1"%slug(job))

    @http.route('''/jobs/detail/<model("hr.job"):job>''',type='http',auth="public",website=True,sitemap=True)
    defjobs_detail(self,job,**kwargs):
        ifnotjob.can_access_from_current_website():
            raiseNotFound()

        returnrequest.render("website_hr_recruitment.detail",{
            'job':job,
            'main_object':job,
        })

    @http.route('''/jobs/apply/<model("hr.job"):job>''',type='http',auth="public",website=True,sitemap=True)
    defjobs_apply(self,job,**kwargs):
        ifnotjob.can_access_from_current_website():
            raiseNotFound()

        error={}
        default={}
        if'website_hr_recruitment_error'inrequest.session:
            error=request.session.pop('website_hr_recruitment_error')
            default=request.session.pop('website_hr_recruitment_default')
        returnrequest.render("website_hr_recruitment.apply",{
            'job':job,
            'error':error,
            'default':default,
        })
