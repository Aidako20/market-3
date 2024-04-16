#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,tools

fromflectra.modulesimportget_resource_path

try:
    importsassaslibsass
exceptImportError:
    #Ifthe`sass`pythonlibraryisn'tfound,wefallbackonthe
    #`sassc`executableinthepath.
    libsass=None
try:
    fromPIL.ImageimportResampling
exceptImportError:
    fromPILimportImageasResampling

DEFAULT_PRIMARY='#000000'
DEFAULT_SECONDARY='#000000'


classBaseDocumentLayout(models.TransientModel):
    """
    Customisethecompanydocumentlayoutanddisplayalivepreview
    """

    _name='base.document.layout'
    _description='CompanyDocumentLayout'

    company_id=fields.Many2one(
        'res.company',default=lambdaself:self.env.company,required=True)

    logo=fields.Binary(related='company_id.logo',readonly=False)
    preview_logo=fields.Binary(related='logo',string="Previewlogo")
    report_header=fields.Text(related='company_id.report_header',readonly=False)
    report_footer=fields.Text(related='company_id.report_footer',readonly=False)

    #Thepaperformatchangeswon'tbereflectedinthepreview.
    paperformat_id=fields.Many2one(related='company_id.paperformat_id',readonly=False)

    external_report_layout_id=fields.Many2one(related='company_id.external_report_layout_id',readonly=False)

    font=fields.Selection(related='company_id.font',readonly=False)
    primary_color=fields.Char(related='company_id.primary_color',readonly=False)
    secondary_color=fields.Char(related='company_id.secondary_color',readonly=False)

    custom_colors=fields.Boolean(compute="_compute_custom_colors",readonly=False)
    logo_primary_color=fields.Char(compute="_compute_logo_colors")
    logo_secondary_color=fields.Char(compute="_compute_logo_colors")

    report_layout_id=fields.Many2one('report.layout')

    #Allthesanitizationgetdisabledaswewanttruerawhtmltobepassedtoaniframe.
    preview=fields.Html(compute='_compute_preview',
                          sanitize=False,
                          sanitize_tags=False,
                          sanitize_attributes=False,
                          sanitize_style=False,
                          sanitize_form=False,
                          strip_style=False,
                          strip_classes=False)

    #Thosefollowingfieldsarerequiredasacompanytocreateinvoicereport
    partner_id=fields.Many2one(related='company_id.partner_id',readonly=True)
    phone=fields.Char(related='company_id.phone',readonly=True)
    email=fields.Char(related='company_id.email',readonly=True)
    website=fields.Char(related='company_id.website',readonly=True)
    vat=fields.Char(related='company_id.vat',readonly=True)
    name=fields.Char(related='company_id.name',readonly=True)
    country_id=fields.Many2one(related="company_id.country_id",readonly=True)

    @api.depends('logo_primary_color','logo_secondary_color','primary_color','secondary_color',)
    def_compute_custom_colors(self):
        forwizardinself:
            logo_primary=wizard.logo_primary_coloror''
            logo_secondary=wizard.logo_secondary_coloror''
            #ForcelowercaseoncolortoensurethatFF01AA==ff01aa
            wizard.custom_colors=(
                wizard.logoandwizard.primary_colorandwizard.secondary_color
                andnot(
                    wizard.primary_color.lower()==logo_primary.lower()
                    andwizard.secondary_color.lower()==logo_secondary.lower()
                )
            )

    @api.depends('logo')
    def_compute_logo_colors(self):
        forwizardinself:
            ifwizard._context.get('bin_size'):
                wizard_for_image=wizard.with_context(bin_size=False)
            else:
                wizard_for_image=wizard
            wizard.logo_primary_color,wizard.logo_secondary_color=wizard_for_image._parse_logo_colors()

    @api.depends('report_layout_id','logo','font','primary_color','secondary_color','report_header','report_footer')
    def_compute_preview(self):
        """computeaqwebbasedpreviewtodisplayonthewizard"""

        styles=self._get_asset_style()

        forwizardinself:
            ifwizard.report_layout_id:
                preview_css=self._get_css_for_preview(styles,wizard.id)
                ir_ui_view=wizard.env['ir.ui.view']
                wizard.preview=ir_ui_view._render_template('web.report_invoice_wizard_preview',{'company':wizard,'preview_css':preview_css})
            else:
                wizard.preview=False

    @api.onchange('company_id')
    def_onchange_company_id(self):
        forwizardinself:
            wizard.logo=wizard.company_id.logo
            wizard.report_header=wizard.company_id.report_header
            wizard.report_footer=wizard.company_id.report_footer
            wizard.paperformat_id=wizard.company_id.paperformat_id
            wizard.external_report_layout_id=wizard.company_id.external_report_layout_id
            wizard.font=wizard.company_id.font
            wizard.primary_color=wizard.company_id.primary_color
            wizard.secondary_color=wizard.company_id.secondary_color
            wizard_layout=wizard.env["report.layout"].search([
                ('view_id.key','=',wizard.company_id.external_report_layout_id.key)
            ])
            wizard.report_layout_id=wizard_layoutorwizard_layout.search([],limit=1)

            ifnotwizard.primary_color:
                wizard.primary_color=wizard.logo_primary_colororDEFAULT_PRIMARY
            ifnotwizard.secondary_color:
                wizard.secondary_color=wizard.logo_secondary_colororDEFAULT_SECONDARY

    @api.onchange('custom_colors')
    def_onchange_custom_colors(self):
        forwizardinself:
            ifwizard.logoandnotwizard.custom_colors:
                wizard.primary_color=wizard.logo_primary_colororDEFAULT_PRIMARY
                wizard.secondary_color=wizard.logo_secondary_colororDEFAULT_SECONDARY

    @api.onchange('report_layout_id')
    def_onchange_report_layout_id(self):
        forwizardinself:
            wizard.external_report_layout_id=wizard.report_layout_id.view_id

    @api.onchange('logo')
    def_onchange_logo(self):
        forwizardinself:
            #Itisadmittedthatiftheuserputstheoriginalimageback,itwon'tchangecolors
            company=wizard.company_id
            #atthatpointwizard.logohasbeenassignedthevaluepresentinDB
            ifwizard.logo==company.logoandcompany.primary_colorandcompany.secondary_color:
                continue

            ifwizard.logo_primary_color:
                wizard.primary_color=wizard.logo_primary_color
            ifwizard.logo_secondary_color:
                wizard.secondary_color=wizard.logo_secondary_color

    def_parse_logo_colors(self,logo=None,white_threshold=225):
        """
        Identifiesdominantcolors

        Firstresizestheoriginalimagetoimproveperformance,thendiscards
        transparentcolorsandwhite-ishcolors,thencallstheaveraging
        methodtwicetoevaluatebothprimaryandsecondarycolors.

        :paramlogo:alternatelogotoprocess
        :paramwhite_threshold:arbitraryvaluedefiningthemaximumvalueacolorcanreach

        :returncolors:hexvaluesofprimaryandsecondarycolors
        """
        self.ensure_one()
        logo=logoorself.logo
        ifnotlogo:
            returnFalse,False

        #The"==="givesdifferentbase64encodingacorrectpadding
        logo+=b'==='ifisinstance(logo,bytes)else'==='
        try:
            #Catchesexceptionscausedbylogonotbeinganimage
            image=tools.image_fix_orientation(tools.base64_to_image(logo))
        exceptException:
            returnFalse,False

        base_w,base_h=image.size
        w=int(50*base_w/base_h)
        h=50

        #ConvertstoRGBA(ifalreadyRGBA,thisisanoop)
        image_converted=image.convert('RGBA')
        image_resized=image_converted.resize((w,h),resample=Resampling.NEAREST)

        colors=[]
        forcolorinimage_resized.getcolors(w*h):
            ifnot(color[1][0]>white_thresholdand
                   color[1][1]>white_thresholdand
                   color[1][2]>white_threshold)andcolor[1][3]>0:
                colors.append(color)

        ifnotcolors: #Mayhappenwhenthewholeimageiswhite
            returnFalse,False
        primary,remaining=tools.average_dominant_color(colors)
        secondary=tools.average_dominant_color(
            remaining)[0]iflen(remaining)>0elseprimary

        #Lightnessandsaturationarecalculatedhere.
        #-Ifbothcolorshaveasimilarlightness,themostcolorfulbecomesprimary
        #-Whenthedifferenceinlightnessistoogreat,thebrightestcolorbecomesprimary
        l_primary=tools.get_lightness(primary)
        l_secondary=tools.get_lightness(secondary)
        if(l_primary<0.2andl_secondary<0.2)or(l_primary>=0.2andl_secondary>=0.2):
            s_primary=tools.get_saturation(primary)
            s_secondary=tools.get_saturation(secondary)
            ifs_primary<s_secondary:
                primary,secondary=secondary,primary
        elifl_secondary>l_primary:
            primary,secondary=secondary,primary

        returntools.rgb_to_hex(primary),tools.rgb_to_hex(secondary)

    @api.model
    defaction_open_base_document_layout(self,action_ref=None):
        ifnotaction_ref:
            action_ref='web.action_base_document_layout_configurator'
        res=self.env["ir.actions.actions"]._for_xml_id(action_ref)
        self.env[res["res_model"]].check_access_rights('write')
        returnres

    defdocument_layout_save(self):
        #meanttobeoverridden
        returnself.env.context.get('report_action')or{'type':'ir.actions.act_window_close'}

    def_get_asset_style(self):
        """
        Compilethestyletemplate.Itisaqwebtemplateexpectingcompanyidstogenerateallthecodeinonebatch.
        Wegiveauselesscompany_idsarg,butprovidethePREVIEW_IDargthatwillpreparethetemplatefor
        '_get_css_for_preview'processinglater.
        :return:
        """
        template_style=self.env.ref('web.styles_company_report',raise_if_not_found=False)
        ifnottemplate_style:
            returnb''

        company_styles=template_style._render({
            'company_ids':self,
        })

        returncompany_styles

    @api.model
    def_get_css_for_preview(self,scss,new_id):
        """
        Compilethescssintocss.
        """
        css_code=self._compile_scss(scss)
        returncss_code

    @api.model
    def_compile_scss(self,scss_source):
        """
        Thiscodewillcompilevalidscssintocss.
        Parametersarethesamefromflectra/addons/base/models/assetsbundle.py
        Simplycopiedandadaptedslightly
        """

        #Noscss?stillvalid,returnsemptycss
        ifnotscss_source.strip():
            return""

        precision=8
        output_style='expanded'
        bootstrap_path=get_resource_path('web','static','lib','bootstrap','scss')

        try:
            returnlibsass.compile(
                string=scss_source,
                include_paths=[
                    bootstrap_path,
                ],
                output_style=output_style,
                precision=precision,
            )
        exceptlibsass.CompileErrorase:
            raiselibsass.CompileError(e.args[0])
