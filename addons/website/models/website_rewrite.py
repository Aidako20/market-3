#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
importwerkzeug

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportAccessDenied,ValidationError

importlogging
_logger=logging.getLogger(__name__)


classWebsiteRoute(models.Model):
    _rec_name='path'
    _name='website.route'
    _description="AllWebsiteRoute"
    _order='path'

    path=fields.Char('Route')

    @api.model
    def_name_search(self,name='',args=None,operator='ilike',limit=100,name_get_uid=None):
        res=super(WebsiteRoute,self)._name_search(name=name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)
        ifnotlen(res):
            self._refresh()
            returnsuper(WebsiteRoute,self)._name_search(name=name,args=args,operator=operator,limit=limit,name_get_uid=name_get_uid)
        returnres

    def_refresh(self):
        _logger.debug("Refreshingwebsite.route")
        ir_http=self.env['ir.http']
        tocreate=[]
        paths={rec.path:recforrecinself.search([])}
        forurl,_,routinginir_http._generate_routing_rules(self.pool._init_modules,converters=ir_http._get_converters()):
            if'GET'in(routing.get('methods')or['GET']):
                ifpaths.get(url):
                    paths.pop(url)
                else:
                    tocreate.append({'path':url})

        iftocreate:
            _logger.info("Add%dwebsite.route"%len(tocreate))
            self.create(tocreate)

        ifpaths:
            find=self.search([('path','in',list(paths.keys()))])
            _logger.info("Delete%dwebsite.route"%len(find))
            find.unlink()


classWebsiteRewrite(models.Model):
    _name='website.rewrite'
    _description="Websiterewrite"

    name=fields.Char('Name',required=True)
    website_id=fields.Many2one('website',string="Website",ondelete='cascade',index=True)
    active=fields.Boolean(default=True)
    url_from=fields.Char('URLfrom',index=True)
    route_id=fields.Many2one('website.route')
    url_to=fields.Char("URLto")
    redirect_type=fields.Selection([
        ('404','404NotFound'),
        ('301','301Movedpermanently'),
        ('302','302Movedtemporarily'),
        ('308','308Redirect/Rewrite'),
    ],string='Action',default="302",
        help='''Typeofredirect/Rewrite:\n
        301Movedpermanently:Thebrowserwillkeepincachethenewurl.
        302Movedtemporarily:Thebrowserwillnotkeepincachethenewurlandaskagainthenexttimethenewurl.
        404NotFound:Ifyouwantremoveaspecificpage/controller(e.g.Ecommerceisinstalled,butyoudon'twant/shoponaspecificwebsite)
        308Redirect/Rewrite:Ifyouwantrenameacontrollerwithanewurl.(Eg:/shop->/garden-Bothurlwillbeaccessiblebut/shopwillautomaticallyberedirectedto/garden)
    ''')

    sequence=fields.Integer()

    @api.onchange('route_id')
    def_onchange_route_id(self):
        self.url_from=self.route_id.path
        self.url_to=self.route_id.path

    @api.constrains('url_to','url_from','redirect_type')
    def_check_url_to(self):
        forrewriteinself:
            ifrewrite.redirect_typein['301','302','308']:
                ifnotrewrite.url_to:
                    raiseValidationError(_('"URLto"cannotbeempty.'))
                ifnotrewrite.url_from:
                    raiseValidationError(_('"URLfrom"cannotbeempty.'))

            ifrewrite.redirect_type=='308':
                ifnotrewrite.url_to.startswith('/'):
                    raiseValidationError(_('"URLto"muststartwithaleadingslash.'))
                forparaminre.findall('/<.*?>',rewrite.url_from):
                    ifparamnotinrewrite.url_to:
                        raiseValidationError(_('"URLto"mustcontainparameter%susedin"URLfrom".')%param)
                forparaminre.findall('/<.*?>',rewrite.url_to):
                    ifparamnotinrewrite.url_from:
                        raiseValidationError(_('"URLto"cannotcontainparameter%swhichisnotusedin"URLfrom".')%param)
                try:
                    converters=self.env['ir.http']._get_converters()
                    routing_map=werkzeug.routing.Map(strict_slashes=False,converters=converters)
                    rule=werkzeug.routing.Rule(rewrite.url_to)
                    routing_map.add(rule)
                exceptValueErrorase:
                    raiseValidationError(_('"URLto"isinvalid:%s')%e)

    defname_get(self):
        result=[]
        forrewriteinself:
            name="%s-%s"%(rewrite.redirect_type,rewrite.name)
            result.append((rewrite.id,name))
        returnresult

    @api.model
    defcreate(self,vals):
        res=super(WebsiteRewrite,self).create(vals)
        self._invalidate_routing()
        returnres

    defwrite(self,vals):
        res=super(WebsiteRewrite,self).write(vals)
        self._invalidate_routing()
        returnres

    defunlink(self):
        res=super(WebsiteRewrite,self).unlink()
        self._invalidate_routing()
        returnres

    def_invalidate_routing(self):
        #callclear_cachesonthisworkertoreloadroutingtable
        self.env['ir.http'].clear_caches()

    defrefresh_routes(self):
        self.env['website.route']._refresh()
