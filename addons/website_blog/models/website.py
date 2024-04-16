#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.addons.http_routing.models.ir_httpimporturl_for


classWebsite(models.Model):
    _inherit="website"

    @api.model
    defpage_search_dependencies(self,page_id=False):
        dep=super(Website,self).page_search_dependencies(page_id=page_id)

        page=self.env['website.page'].browse(int(page_id))
        path=page.url

        dom=[
            ('content','ilike',path)
        ]
        posts=self.env['blog.post'].search(dom)
        ifposts:
            page_key=_('BlogPost')
            iflen(posts)>1:
                page_key=_('BlogPosts')
            dep[page_key]=[]
        forpinposts:
            dep[page_key].append({
                'text':_('BlogPost<b>%s</b>seemstohavealinktothispage!',p.name),
                'item':p.name,
                'link':p.website_url,
            })

        returndep

    @api.model
    defpage_search_key_dependencies(self,page_id=False):
        dep=super(Website,self).page_search_key_dependencies(page_id=page_id)

        page=self.env['website.page'].browse(int(page_id))
        key=page.key

        dom=[
            ('content','ilike',key)
        ]
        posts=self.env['blog.post'].search(dom)
        ifposts:
            page_key=_('BlogPost')
            iflen(posts)>1:
                page_key=_('BlogPosts')
            dep[page_key]=[]
        forpinposts:
            dep[page_key].append({
                'text':_('BlogPost<b>%s</b>seemstobecallingthisfile!',p.name),
                'item':p.name,
                'link':p.website_url,
            })

        returndep

    defget_suggested_controllers(self):
        suggested_controllers=super(Website,self).get_suggested_controllers()
        suggested_controllers.append((_('Blog'),url_for('/blog'),'website_blog'))
        returnsuggested_controllers
