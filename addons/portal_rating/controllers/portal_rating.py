#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp,_
fromflectra.httpimportrequest


classPortalRating(http.Controller):

    @http.route(['/website/rating/comment'],type='json',auth="user",methods=['POST'],website=True)
    defpublish_rating_comment(self,rating_id,publisher_comment):
        rating=request.env['rating.rating'].search([('id','=',int(rating_id))])
        ifnotrating:
            return{'error':_('Invalidrating')}
        rating.write({'publisher_comment':publisher_comment})
        #returntothefront-endthecreated/updatedpublishercomment
        returnrating.read(['publisher_comment','publisher_id','publisher_datetime'])[0]
