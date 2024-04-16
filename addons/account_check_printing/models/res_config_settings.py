#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    account_check_printing_layout=fields.Selection(
        related='company_id.account_check_printing_layout',
        string="CheckLayout",
        readonly=False,
        help="Selecttheformatcorrespondingtothecheckpaperyouwillbeprintingyourcheckson.\n"
             "Inordertodisabletheprintingfeature,select'None'."
    )
    account_check_printing_date_label=fields.Boolean(
        related='company_id.account_check_printing_date_label',
        string="PrintDateLabel",
        readonly=False,
        help="ThisoptionallowsyoutoprintthedatelabelonthecheckasperCPA.\n"
             "Disablethisifyourpre-printedcheckincludesthedatelabel."
    )
    account_check_printing_multi_stub=fields.Boolean(
        related='company_id.account_check_printing_multi_stub',
        string='Multi-PagesCheckStub',
        readonly=False,
        help="Thisoptionallowsyoutoprintcheckdetails(stub)onmultiplepagesiftheydon'tfitonasinglepage."
    )
    account_check_printing_margin_top=fields.Float(
        related='company_id.account_check_printing_margin_top',
        string='CheckTopMargin',
        readonly=False,
        help="Adjustthemarginsofgeneratedcheckstomakeitfityourprinter'ssettings."
    )
    account_check_printing_margin_left=fields.Float(
        related='company_id.account_check_printing_margin_left',
        string='CheckLeftMargin',
        readonly=False,
        help="Adjustthemarginsofgeneratedcheckstomakeitfityourprinter'ssettings."
    )
    account_check_printing_margin_right=fields.Float(
        related='company_id.account_check_printing_margin_right',
        string='CheckRightMargin',
        readonly=False,
        help="Adjustthemarginsofgeneratedcheckstomakeitfityourprinter'ssettings."
    )
