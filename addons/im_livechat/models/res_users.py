#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classUsers(models.Model):
    """Updateofres.usersclass
        -addapreferenceaboutusernameforlivechatpurpose
    """
    _inherit='res.users'

    livechat_username=fields.Char("LivechatUsername",help="Thisusernamewillbeusedasyournameinthelivechatchannels.")

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrightsonlivechat_username
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res=super(Users,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_WRITEABLE_FIELDS=list(self.SELF_WRITEABLE_FIELDS)
        pool[self._name].SELF_WRITEABLE_FIELDS.extend(['livechat_username'])
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=list(self.SELF_READABLE_FIELDS)
        pool[self._name].SELF_READABLE_FIELDS.extend(['livechat_username'])
        returninit_res
