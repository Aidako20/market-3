#-*-coding:utf-8-*-

fromflectraimportfields,models,exceptions,_


classRating(models.Model):
    _inherit='rating.rating'

    #Addinginformationforcommentaratingmessage
    publisher_comment=fields.Text("Publishercomment")
    publisher_id=fields.Many2one('res.partner','Commentedby',
                                   ondelete='setnull',readonly=True)
    publisher_datetime=fields.Datetime("Commentedon",readonly=True)

    defwrite(self,values):
        ifvalues.get('publisher_comment'):
            ifnotself.env.user.has_group("website.group_website_publisher"):
                raiseexceptions.AccessError(_("Onlythepublisherofthewebsitecanchangetheratingcomment"))
            ifnotvalues.get('publisher_datetime'):
                values['publisher_datetime']=fields.Datetime.now()
            ifnotvalues.get('publisher_id'):
                values['publisher_id']=self.env.user.partner_id.id
        returnsuper(Rating,self).write(values)
