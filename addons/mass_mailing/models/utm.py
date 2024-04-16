#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classUtmCampaign(models.Model):
    _inherit='utm.campaign'

    mailing_mail_ids=fields.One2many(
        'mailing.mailing','campaign_id',
        domain=[('mailing_type','=','mail')],
        string='MassMailings')
    mailing_mail_count=fields.Integer('NumberofMassMailing',compute="_compute_mailing_mail_count")
    #statfields
    received_ratio=fields.Integer(compute="_compute_statistics",string='ReceivedRatio')
    opened_ratio=fields.Integer(compute="_compute_statistics",string='OpenedRatio')
    replied_ratio=fields.Integer(compute="_compute_statistics",string='RepliedRatio')
    bounced_ratio=fields.Integer(compute="_compute_statistics",string='BouncedRatio')

    @api.depends('mailing_mail_ids')
    def_compute_mailing_mail_count(self):
        ifself.ids:
            mailing_data=self.env['mailing.mailing'].read_group(
                [('campaign_id','in',self.ids),('mailing_type','=','mail')],
                ['campaign_id'],
                ['campaign_id']
            )
            mapped_data={m['campaign_id'][0]:m['campaign_id_count']forminmailing_data}
        else:
            mapped_data=dict()
        forcampaigninself:
            campaign.mailing_mail_count=mapped_data.get(campaign.id,0)

    def_compute_statistics(self):
        """Computestatisticsofthemassmailingcampaign"""
        default_vals={
            'received_ratio':0,
            'opened_ratio':0,
            'replied_ratio':0,
            'bounced_ratio':0
        }
        ifnotself.ids:
            self.update(default_vals)
            return
        self.env.cr.execute("""
            SELECT
                c.idascampaign_id,
                COUNT(s.id)ASexpected,
                COUNT(CASEWHENs.sentisnotnullTHEN1ELSEnullEND)ASsent,
                COUNT(CASEWHENs.scheduledisnotnullANDs.sentisnullANDs.exceptionisnullANDs.ignoredisnotnullTHEN1ELSEnullEND)ASignored,
                COUNT(CASEWHENs.idisnotnullANDs.bouncedisnullTHEN1ELSEnullEND)ASdelivered,
                COUNT(CASEWHENs.openedisnotnullTHEN1ELSEnullEND)ASopened,
                COUNT(CASEWHENs.repliedisnotnullTHEN1ELSEnullEND)ASreplied,
                COUNT(CASEWHENs.bouncedisnotnullTHEN1ELSEnullEND)ASbounced
            FROM
                mailing_traces
            RIGHTJOIN
                utm_campaignc
                ON(c.id=s.campaign_id)
            WHERE
                c.idIN%s
            GROUPBY
                c.id
        """,(tuple(self.ids),))

        all_stats=self.env.cr.dictfetchall()
        stats_per_campaign={
            stats['campaign_id']:stats
            forstatsinall_stats
        }

        forcampaigninself:
            stats=stats_per_campaign.get(campaign.id)
            ifnotstats:
                vals=default_vals
            else:
                total=(stats['expected']-stats['ignored'])or1
                delivered=stats['sent']-stats['bounced']
                vals={
                    'received_ratio':100.0*delivered/total,
                    'opened_ratio':100.0*stats['opened']/total,
                    'replied_ratio':100.0*stats['replied']/total,
                    'bounced_ratio':100.0*stats['bounced']/total
                }

            campaign.update(vals)

    def_get_mailing_recipients(self,model=None):
        """Returntherecipientsofamailingcampaign.Thisisbasedonthestatistics
        buildforeachmailing."""
        res=dict.fromkeys(self.ids,{})
        forcampaigninself:
            domain=[('campaign_id','=',campaign.id)]
            ifmodel:
                domain+=[('model','=',model)]
            res[campaign.id]=set(self.env['mailing.trace'].search(domain).mapped('res_id'))
        returnres
