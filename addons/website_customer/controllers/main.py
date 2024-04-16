#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug.urls

fromflectraimporthttp
fromflectra.addons.http_routing.models.ir_httpimportunslug,slug
fromflectra.addons.website.models.ir_httpimportsitemap_qs2dom
fromflectra.tools.translateimport_
fromflectra.httpimportrequest


classWebsiteCustomer(http.Controller):
    _references_per_page=20

    defsitemap_industry(env,rule,qs):
        ifnotqsorqs.lower()in'/customers':
            yield{'loc':'/customers'}

        Industry=env['res.partner.industry']
        dom=sitemap_qs2dom(qs,'/customers/industry',Industry._rec_name)
        forindustryinIndustry.search(dom):
            loc='/customers/industry/%s'%slug(industry)
            ifnotqsorqs.lower()inloc:
                yield{'loc':loc}

        dom=[('website_published','=',True),('assigned_partner_id','!=',False),('country_id','!=',False)]
        dom+=sitemap_qs2dom(qs,'/customers/country')
        countries=env['res.partner'].sudo().read_group(dom,['id','country_id'],groupby='country_id')
        forcountryincountries:
            loc='/customers/country/%s'%slug(country['country_id'])
            ifnotqsorqs.lower()inloc:
                yield{'loc':loc}

    @http.route([
        '/customers',
        '/customers/page/<int:page>',
        '/customers/country/<model("res.country"):country>',
        '/customers/country/<model("res.country"):country>/page/<int:page>',
        '/customers/industry/<model("res.partner.industry"):industry>',
        '/customers/industry/<model("res.partner.industry"):industry>/page/<int:page>',
        '/customers/industry/<model("res.partner.industry"):industry>/country/<model("res.country"):country>',
        '/customers/industry/<model("res.partner.industry"):industry>/country/<model("res.country"):country>/page/<int:page>',
    ],type='http',auth="public",website=True,sitemap=sitemap_industry)
    defcustomers(self,country=None,industry=None,page=0,**post):
        Tag=request.env['res.partner.tag']
        Partner=request.env['res.partner']
        search_value=post.get('search')

        domain=[('website_published','=',True),('assigned_partner_id','!=',False)]
        ifsearch_value:
            domain+=[
                '|','|',
                ('name','ilike',search_value),
                ('website_description','ilike',search_value),
                ('industry_id.name','ilike',search_value),
            ]

        tag_id=post.get('tag_id')
        iftag_id:
            tag_id=unslug(tag_id)[1]or0
            domain+=[('website_tag_ids','in',tag_id)]

        #groupbyindustry,basedoncustomersfoundwiththesearch(domain)
        industries=Partner.sudo().read_group(domain,["id","industry_id"],groupby="industry_id",orderby="industry_id")
        partners_count=Partner.sudo().search_count(domain)

        ifindustry:
            domain.append(('industry_id','=',industry.id))
            ifindustry.idnotin(x['industry_id'][0]forxinindustriesifx['industry_id']):
                ifindustry.exists():
                    industries.append({
                        'industry_id_count':0,
                        'industry_id':(industry.id,industry.name)
                    })

        industries.sort(key=lambdad:(d.get('industry_id')or(0,''))[1])

        industries.insert(0,{
            'industry_id_count':partners_count,
            'industry_id':(0,_("AllIndustries"))
        })

        #groupbycountry,basedoncustomersfoundwiththesearch(domain)
        countries=Partner.sudo().read_group(domain,["id","country_id"],groupby="country_id",orderby="country_id")
        country_count=Partner.sudo().search_count(domain)

        ifcountry:
            domain+=[('country_id','=',country.id)]
            ifcountry.idnotin(x['country_id'][0]forxincountriesifx['country_id']):
                ifcountry.exists():
                    countries.append({
                        'country_id_count':0,
                        'country_id':(country.id,country.name)
                    })
                    countries.sort(key=lambdad:(d['country_id']or(0,""))[1])

        countries.insert(0,{
            'country_id_count':country_count,
            'country_id':(0,_("AllCountries"))
        })

        #searchcustomerstodisplay
        partner_count=Partner.sudo().search_count(domain)

        #pager
        url='/customers'
        ifindustry:
            url+='/industry/%s'%industry.id
        ifcountry:
            url+='/country/%s'%country.id
        pager=request.website.pager(
            url=url,total=partner_count,page=page,step=self._references_per_page,
            scope=7,url_args=post
        )

        partners=Partner.sudo().search(domain,offset=pager['offset'],limit=self._references_per_page)
        google_map_partner_ids=','.join(str(it)foritinpartners.ids)
        google_maps_api_key=request.website.google_maps_api_key

        tags=Tag.search([('website_published','=',True),('partner_ids','in',partners.ids)],order='classname,nameASC')
        tag=tag_idandTag.browse(tag_id)orFalse

        values={
            'countries':countries,
            'current_country_id':country.idifcountryelse0,
            'current_country':countryorFalse,
            'industries':industries,
            'current_industry_id':industry.idifindustryelse0,
            'current_industry':industryorFalse,
            'partners':partners,
            'google_map_partner_ids':google_map_partner_ids,
            'pager':pager,
            'post':post,
            'search_path':"?%s"%werkzeug.urls.url_encode(post),
            'tag':tag,
            'tags':tags,
            'google_maps_api_key':google_maps_api_key,
        }
        returnrequest.render("website_customer.index",values)

    #DonotusesemanticcontrollerduetoSUPERUSER_ID
    @http.route(['/customers/<partner_id>'],type='http',auth="public",website=True)
    defpartners_detail(self,partner_id,**post):
        _,partner_id=unslug(partner_id)
        ifpartner_id:
            partner=request.env['res.partner'].sudo().browse(partner_id)
            ifpartner.exists()andpartner.website_published:
                values={}
                values['main_object']=values['partner']=partner
                returnrequest.render("website_customer.details",values)
        returnself.customers(**post)
