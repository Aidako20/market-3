#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.tools.translateimport_


classWebsiteBackend(http.Controller):

    @http.route('/website/fetch_dashboard_data',type="json",auth='user')
    deffetch_dashboard_data(self,website_id,date_from,date_to):
        Website=request.env['website']
        has_group_system=request.env.user.has_group('base.group_system')
        has_group_designer=request.env.user.has_group('website.group_website_designer')
        dashboard_data={
            'groups':{
                'system':has_group_system,
                'website_designer':has_group_designer
            },
            'currency':request.env.company.currency_id.id,
            'dashboards':{
                'visits':{},
            }
        }

        current_website=website_idandWebsite.browse(website_id)orWebsite.get_current_website()
        multi_website=request.env.user.has_group('website.group_multi_website')
        websites=multi_websiteandrequest.env['website'].search([])orcurrent_website
        dashboard_data['websites']=websites.read(['id','name'])
        forrec,websiteinzip(websites,dashboard_data['websites']):
            website['domain']=rec._get_http_domain()
            ifwebsite['id']==current_website.id:
                website['selected']=True

        ifhas_group_designer:
            ifcurrent_website.google_management_client_idandcurrent_website.google_analytics_key:
                dashboard_data['dashboards']['visits']=dict(
                    ga_client_id=current_website.google_management_client_idor'',
                    ga_analytics_key=current_website.google_analytics_keyor'',
                )
        returndashboard_data

    @http.route('/website/dashboard/set_ga_data',type='json',auth='user')
    defwebsite_set_ga_data(self,website_id,ga_client_id,ga_analytics_key):
        ifnotrequest.env.user.has_group('base.group_system'):
            return{
                'error':{
                    'title':_('AccessError'),
                    'message':_('Youdonothavesufficientrightstoperformthataction.'),
                }
            }
        ifnotga_analytics_keyornotga_client_id.endswith('.apps.googleusercontent.com'):
            return{
                'error':{
                    'title':_('IncorrectClientID/Key'),
                    'message':_('TheGoogleAnalyticsClientIDorKeyyouenteredseemsincorrect.'),
                }
            }
        Website=request.env['website']
        current_website=website_idandWebsite.browse(website_id)orWebsite.get_current_website()

        request.env['res.config.settings'].create({
            'google_management_client_id':ga_client_id,
            'google_analytics_key':ga_analytics_key,
            'website_id':current_website.id,
        }).execute()
        returnTrue
