#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest


classWebsiteUrl(http.Controller):
    @http.route('/website_links/new',type='json',auth='user',methods=['POST'])
    defcreate_shorten_url(self,**post):
        if'url'notinpostorpost['url']=='':
            return{'error':'empty_url'}
        returnrequest.env['link.tracker'].create(post).read()

    @http.route('/r',type='http',auth='user',website=True)
    defshorten_url(self,**post):
        returnrequest.render("website_links.page_shorten_url",post)

    @http.route('/website_links/add_code',type='json',auth='user')
    defadd_code(self,**post):
        link_id=request.env['link.tracker.code'].search([('code','=',post['init_code'])],limit=1).link_id.id
        new_code=request.env['link.tracker.code'].search_count([('code','=',post['new_code']),('link_id','=',link_id)])
        ifnew_code>0:
            returnnew_code.read()
        else:
            returnrequest.env['link.tracker.code'].create({'code':post['new_code'],'link_id':link_id})[0].read()

    @http.route('/website_links/recent_links',type='json',auth='user')
    defrecent_links(self,**post):
        returnrequest.env['link.tracker'].recent_links(post['filter'],post['limit'])

    @http.route('/r/<string:code>+',type='http',auth="user",website=True)
    defstatistics_shorten_url(self,code,**post):
        code=request.env['link.tracker.code'].search([('code','=',code)],limit=1)

        ifcode:
            returnrequest.render("website_links.graphs",code.link_id.read()[0])
        else:
            returnwerkzeug.utils.redirect('/',301)
