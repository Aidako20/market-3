#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug.urls

fromflectraimportfields

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.http_routing.models.ir_httpimportunslug
fromflectra.tools.translateimport_


classWebsiteMembership(http.Controller):
    _references_per_page=20

    @http.route([
        '/members',
        '/members/page/<int:page>',
        '/members/association/<membership_id>',
        '/members/association/<membership_id>/page/<int:page>',

        '/members/country/<int:country_id>',
        '/members/country/<country_name>-<int:country_id>',
        '/members/country/<int:country_id>/page/<int:page>',
        '/members/country/<country_name>-<int:country_id>/page/<int:page>',

        '/members/association/<membership_id>/country/<country_name>-<int:country_id>',
        '/members/association/<membership_id>/country/<int:country_id>',
        '/members/association/<membership_id>/country/<country_name>-<int:country_id>/page/<int:page>',
        '/members/association/<membership_id>/country/<int:country_id>/page/<int:page>',
    ],type='http',auth="public",website=True,sitemap=True)
    defmembers(self,membership_id=None,country_name=None,country_id=0,page=1,**post):
        Product=request.env['product.product']
        Country=request.env['res.country']
        MembershipLine=request.env['membership.membership_line']
        Partner=request.env['res.partner']

        post_name=post.get('search')orpost.get('name','')
        current_country=None
        today=fields.Date.today()

        #basedomainforgroupby/searches
        base_line_domain=[
            ("partner.website_published","=",True),('state','=','paid'),
            ('date_to','>=',today),('date_from','<=',today)
        ]
        ifmembership_idandmembership_id!='free':
            membership_id=int(membership_id)
            base_line_domain.append(('membership_id','=',membership_id))

        ifpost_name:
            base_line_domain+=['|',('partner.name','ilike',post_name),('partner.website_description','ilike',post_name)]

        #groupbycountry,basedonallcustomers(basedomain)
        ifmembership_id!='free':
            membership_lines=MembershipLine.sudo().search(base_line_domain)
            country_domain=[('member_lines','in',membership_lines.ids)]
            ifnotmembership_id:
                country_domain=['|',country_domain[0],('membership_state','=','free')]
        else:
            country_domain=[('membership_state','=','free')]
        ifpost_name:
            country_domain+=['|',('name','ilike',post_name),('website_description','ilike',post_name)]

        countries=Partner.sudo().read_group(country_domain+[("website_published","=",True)],["id","country_id"],groupby="country_id",orderby="country_id")
        countries_total=sum(country_dict['country_id_count']forcountry_dictincountries)

        line_domain=list(base_line_domain)
        ifcountry_id:
            line_domain.append(('partner.country_id','=',country_id))
            current_country=Country.browse(country_id).read(['id','name'])[0]
            ifnotany(x['country_id'][0]==country_idforxincountriesifx['country_id']):
                countries.append({
                    'country_id_count':0,
                    'country_id':(country_id,current_country["name"])
                })
                countries=[dfordincountriesifd['country_id']]
                countries.sort(key=lambdad:d['country_id'][1])

        countries.insert(0,{
            'country_id_count':countries_total,
            'country_id':(0,_("AllCountries"))
        })

        #formatdomainforgroup_byandmemberships
        memberships=Product.search([('membership','=',True)],order="website_sequence")

        #makesurewedon'taccesstolineswithunpublishedmembershipts
        line_domain.append(('membership_id','in',memberships.ids))

        limit=self._references_per_page
        offset=limit*(page-1)

        count_members=0
        membership_lines=MembershipLine.sudo()
        #displayednon-freemembershiplines
        ifmembership_id!='free':
            count_members=MembershipLine.sudo().search_count(line_domain)
            ifoffset<=count_members:
                membership_lines=MembershipLine.sudo().search(line_domain,offset,limit)
        page_partner_ids=set(m.partner.idforminmembership_lines)

        #getgooglemapslocalizationofpartners
        google_map_partner_ids=[]
        ifrequest.website.is_view_active('website_membership.opt_index_google_map'):
            google_map_partner_ids=MembershipLine.search(line_domain).get_published_companies(limit=2000)

        search_domain=[('membership_state','=','free'),('website_published','=',True)]
        ifpost_name:
            search_domain+=['|',('name','ilike',post_name),('website_description','ilike',post_name)]
        ifcountry_id:
            search_domain+=[('country_id','=',country_id)]
        free_partners=Partner.sudo().search(search_domain)

        memberships_data=[]
        formembership_recordinmemberships:
            memberships_data.append({'id':membership_record.id,'name':membership_record.name})

        memberships_partner_ids={}
        forlineinmembership_lines:
            memberships_partner_ids.setdefault(line.membership_id.id,[]).append(line.partner.id)

        iffree_partners:
            memberships_data.append({'id':'free','name':_('FreeMembers')})
            ifnotmembership_idormembership_id=='free':
                ifcount_members<offset+limit:
                    free_start=max(offset-count_members,0)
                    free_end=max(offset+limit-count_members,0)
                    memberships_partner_ids['free']=free_partners.ids[free_start:free_end]
                    page_partner_ids|=set(memberships_partner_ids['free'])
                google_map_partner_ids+=free_partners.ids[:2000-len(google_map_partner_ids)]
                count_members+=len(free_partners)

        google_map_partner_ids=",".join(str(it)foritingoogle_map_partner_ids)
        google_maps_api_key=request.website.google_maps_api_key

        partners={p.id:pforpinPartner.sudo().browse(list(page_partner_ids))}

        base_url='/members%s%s'%('/association/%s'%membership_idifmembership_idelse'',
                                     '/country/%s'%country_idifcountry_idelse'')

        #requestpagerforlines
        pager=request.website.pager(url=base_url,total=count_members,page=page,step=limit,scope=7,url_args=post)

        values={
            'partners':partners,
            'memberships_data':memberships_data,
            'memberships_partner_ids':memberships_partner_ids,
            'membership_id':membership_id,
            'countries':countries,
            'current_country':current_countryand[current_country['id'],current_country['name']]orNone,
            'current_country_id':current_countryandcurrent_country['id']or0,
            'google_map_partner_ids':google_map_partner_ids,
            'pager':pager,
            'post':post,
            'search':"?%s"%werkzeug.urls.url_encode(post),
            'search_count':count_members,
            'google_maps_api_key':google_maps_api_key,
        }
        returnrequest.render("website_membership.index",values)

    #DonotusesemanticcontrollerduetoSUPERUSER_ID
    @http.route(['/members/<partner_id>'],type='http',auth="public",website=True)
    defpartners_detail(self,partner_id,**post):
        _,partner_id=unslug(partner_id)
        ifpartner_id:
            partner=request.env['res.partner'].sudo().browse(partner_id)
            ifpartner.exists()andpartner.website_published: #TODOshouldbedonewithaccessrules
                values={}
                values['main_object']=values['partner']=partner
                returnrequest.render("website_membership.partner",values)
        returnself.members(**post)
