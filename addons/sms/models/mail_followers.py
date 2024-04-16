#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classFollowers(models.Model):
    _inherit=['mail.followers']

    def_get_recipient_data(self,records,message_type,subtype_id,pids=None,cids=None):
        ifmessage_type=='sms':
            ifpidsisNone:
                sms_pids=records._sms_get_default_partners().ids
            else:
                sms_pids=pids
            res=super(Followers,self)._get_recipient_data(records,message_type,subtype_id,pids=pids,cids=cids)
            new_res=[]
            forpid,cid,pactive,pshare,ctype,notif,groupsinres:
                ifpidandpidinsms_pids:
                    notif='sms'
                new_res.append((pid,cid,pactive,pshare,ctype,notif,groups))
            returnnew_res
        else:
            returnsuper(Followers,self)._get_recipient_data(records,message_type,subtype_id,pids=pids,cids=cids)
