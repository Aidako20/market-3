#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classTour(models.Model):

    _name="web_tour.tour"
    _description="Tours"
    _log_access=False

    name=fields.Char(string="Tourname",required=True)
    user_id=fields.Many2one('res.users',string='Consumedby')

    @api.model
    defconsume(self,tour_names):
        """Setsgiventoursasconsumed,meaningthat
            thesetourswon'tbeactiveanymoreforthatuser"""
        ifnotself.env.user.has_group('base.group_user'):
            #Onlyinternaluserscanusethismethod.
            #TODOmaster:updateir.model.accessrecordsinsteadofusingsudo()
            return
        fornameintour_names:
            self.sudo().create({'name':name,'user_id':self.env.uid})

    @api.model
    defget_consumed_tours(self):
        """Returnsthelistofconsumedtoursforthecurrentuser"""
        return[t.namefortinself.search([('user_id','=',self.env.uid)])]
