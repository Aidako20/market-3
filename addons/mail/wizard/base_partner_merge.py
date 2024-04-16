#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,models,_


classMergePartnerAutomatic(models.TransientModel):

    _inherit='base.partner.merge.automatic.wizard'

    def_log_merge_operation(self,src_partners,dst_partner):
        super(MergePartnerAutomatic,self)._log_merge_operation(src_partners,dst_partner)
        dst_partner.message_post(body='%s%s'%(_("Mergedwiththefollowingpartners:"),",".join('%s<%s>(ID%s)'%(p.name,p.emailor'n/a',p.id)forpinsrc_partners)))
