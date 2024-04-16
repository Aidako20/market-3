#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.httpimportrequest
fromflectra.addons.website_slides.controllers.mainimportWebsiteSlides


classWebsiteSlidesForum(WebsiteSlides):

    def_slide_channel_prepare_values(self,**kwargs):
        channel=super(WebsiteSlidesForum,self)._slide_channel_prepare_values(**kwargs)
        ifbool(kwargs.get('link_forum')):
            forum=request.env['forum.forum'].create({
                'name':kwargs.get('name')
            })
            channel['forum_id']=forum.id
        returnchannel

    #Profile
    #---------------------------------------------------

    def_prepare_user_profile_parameters(self,**post):
        post=super(WebsiteSlidesForum,self)._prepare_user_profile_parameters(**post)
        ifpost.get('channel_id'):
            channel=request.env['slide.channel'].browse(int(post.get('channel_id')))
            ifchannel.forum_id:
                post.update({
                    'forum_id':channel.forum_id.id,
                    'no_forum':False
                })
            else:
                post.update({'no_forum':True})
        returnpost
