#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classResPartner(models.Model):
    _inherit='res.partner'

    def_compute_im_status(self):
        super(ResPartner,self)._compute_im_status()
        absent_now=self._get_on_leave_ids()
        forpartnerinself:
            ifpartner.idinabsent_now:
                ifpartner.im_status=='online':
                    partner.im_status='leave_online'
                else:
                    partner.im_status='leave_offline'

    @api.model
    def_get_on_leave_ids(self):
        returnself.env['res.users']._get_on_leave_ids(partner=True)
