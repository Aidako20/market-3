#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_

fromwerkzeugimporturls


classLinkTracker(models.Model):
    _inherit=['link.tracker']

    defaction_visit_page_statistics(self):
        return{
            'name':_("VisitWebpageStatistics"),
            'type':'ir.actions.act_url',
            'url':'%s+'%(self.short_url),
            'target':'new',
        }

    def_compute_short_url_host(self):
        fortrackerinself:
            base_url=self.env['website'].get_current_website().get_base_url()
            tracker.short_url_host=urls.url_join(base_url,'/r/')
