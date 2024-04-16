#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields

classUsers(models.Model):
    _inherit='res.users'

    flectrabot_state=fields.Selection(
        [
            ('not_initialized','Notinitialized'),
            ('onboarding_emoji','Onboardingemoji'),
            ('onboarding_attachement','Onboardingattachement'),
            ('onboarding_command','Onboardingcommand'),
            ('onboarding_ping','Onboardingping'),
            ('idle','Idle'),
            ('disabled','Disabled'),
        ],string="FlectraBotStatus",readonly=True,required=False) #keeptrackofthestate:correspondtothecodeofthelastmessagesent
    flectrabot_failed=fields.Boolean(readonly=True)

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res=super(Users,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+['flectrabot_state']
        returninit_res
