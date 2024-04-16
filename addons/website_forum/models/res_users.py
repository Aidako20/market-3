#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classUsers(models.Model):
    _inherit='res.users'

    create_date=fields.Datetime('CreateDate',readonly=True,index=True)
    forum_waiting_posts_count=fields.Integer('Waitingpost',compute="_get_user_waiting_post")

    def_get_user_waiting_post(self):
        foruserinself:
            Post=self.env['forum.post']
            domain=[('parent_id','=',False),('state','=','pending'),('create_uid','=',user.id)]
            user.forum_waiting_posts_count=Post.search_count(domain)

    #Wrapperforcall_kwwithinherits
    defopen_website_url(self):
        returnself.mapped('partner_id').open_website_url()

    defget_gamification_redirection_data(self):
        res=super(Users,self).get_gamification_redirection_data()
        res.append({
            'url':'/forum',
            'label':'SeeourForum'
        })
        returnres
