#-*-coding:utf-8-*-

fromflectraimportmodels,fields


classres_company(models.Model):
    _inherit="res.company"

    #Thisfieldneedstobeoverriddenwith`selection_add`inthemoduleswhichintendstoaddreportlayouts.
    #ThexmlIDofallthereportactionswhichareactuallyCheckLayoutshastobekeptaskeyoftheselection.
    account_check_printing_layout=fields.Selection(
        string="CheckLayout",
        selection=[
            ('disabled','None'),
        ],
        default='disabled',
        help="Selecttheformatcorrespondingtothecheckpaperyouwillbeprintingyourcheckson.\n"
             "Inordertodisabletheprintingfeature,select'None'.",
    )
    account_check_printing_date_label=fields.Boolean(
        string='PrintDateLabel',
        default=True,
        help="ThisoptionallowsyoutoprintthedatelabelonthecheckasperCPA.\n"
             "Disablethisifyourpre-printedcheckincludesthedatelabel.",
    )
    account_check_printing_multi_stub=fields.Boolean(
        string='Multi-PagesCheckStub',
        help="Thisoptionallowsyoutoprintcheckdetails(stub)onmultiplepagesiftheydon'tfitonasinglepage.",
    )
    account_check_printing_margin_top=fields.Float(
        string='CheckTopMargin',
        default=0.25,
        help="Adjustthemarginsofgeneratedcheckstomakeitfityourprinter'ssettings.",
    )
    account_check_printing_margin_left=fields.Float(
        string='CheckLeftMargin',
        default=0.25,
        help="Adjustthemarginsofgeneratedcheckstomakeitfityourprinter'ssettings.",
    )
    account_check_printing_margin_right=fields.Float(
        string='RightMargin',
        default=0.25,
        help="Adjustthemarginsofgeneratedcheckstomakeitfityourprinter'ssettings.",
    )
