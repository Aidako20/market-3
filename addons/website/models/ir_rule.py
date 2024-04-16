#coding:utf-8
fromflectraimportapi,models
fromflectra.addons.website.modelsimportir_http


classIrRule(models.Model):
    _inherit='ir.rule'

    @api.model
    def_eval_context(self):
        res=super(IrRule,self)._eval_context()

        #Weneedis_frontendtoavoidshowingwebsite'scompanyitemsinbackend
        #(thatcouldbedifferentthancurrentcompany).Wecan'tuse
        #`get_current_website(falback=False)`asitcouldalsoreturnawebsite
        #inbackend(ifdomainset&match)..
        is_frontend=ir_http.get_request_website()
        Website=self.env['website']
        res['website']=is_frontendandWebsite.get_current_website()orWebsite
        returnres

    def_compute_domain_keys(self):
        """Returnthelistofcontextkeystouseforcaching``_compute_domain``."""
        returnsuper(IrRule,self)._compute_domain_keys()+['website_id']
