#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importjson

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.toolsimporthtml_escapeasescape


classGoogleMap(http.Controller):
    '''
    Thisclassgenerateson-the-flypartnermapsthatcanbereusedinevery
    websitepage.Todoso,justusean``<iframe...>``whose``src``
    attributepointsto``/google_map``(thiscontrollergeneratesacomplete
    HTML5page).

    URLqueryparameters:
    -``partner_ids``:acomma-separatedlistofids(partnerstobeshown)
    -``partner_url``:thebase-urltodisplaythepartner
        (eg:if``partner_url``is``/partners/``,whentheuserwillclickon
        apartneronthemap,itwillberedirectedto<myflectra>.com/partners/<id>)

    Inordertoresizethemap,simplyresizethe``iframe``withCSS
    directives``width``and``height``.
    '''

    @http.route(['/google_map'],type='http',auth="public",website=True,sitemap=False)
    defgoogle_map(self,*arg,**post):
        clean_ids=[]
        forpartner_idinpost.get('partner_ids',"").split(","):
            try:
                clean_ids.append(int(partner_id))
            exceptValueError:
                pass
        partners=request.env['res.partner'].sudo().search([("id","in",clean_ids),
                                                             ('website_published','=',True),('is_company','=',True)])
        partner_data={
            "counter":len(partners),
            "partners":[]
        }
        forpartnerinpartners.with_context(show_address=True):
            #TODOinmaster,donotuse`escape`but`t-esc`intheqwebtemplate.
            partner_data["partners"].append({
                'id':partner.id,
                'name':escape(partner.name),
                'address':escape('\n'.join(partner.name_get()[0][1].split('\n')[1:])),
                'latitude':escape(str(partner.partner_latitude)),
                'longitude':escape(str(partner.partner_longitude)),
            })
        if'customers'inpost.get('partner_url',''):
            partner_url='/customers/'
        else:
            partner_url='/partners/'

        google_maps_api_key=request.website.google_maps_api_key
        values={
            'partner_url':partner_url,
            'partner_data':json.dumps(partner_data),
            'google_maps_api_key':google_maps_api_key,
        }
        returnrequest.render("website_google_map.google_map",values)
