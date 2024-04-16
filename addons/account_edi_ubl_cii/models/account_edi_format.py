#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,_
fromflectra.toolsimportstr2bool
fromflectra.addons.account_edi_ubl_cii.models.account_edi_commonimportCOUNTRY_EAS

importlogging

_logger=logging.getLogger(__name__)

FORMAT_CODES=[
    'facturx_1_0_05',
    'ubl_bis3',
    'ubl_de',
    'nlcius_1',
    'efff_1',
    'ubl_2_1',
    'ehf_3',
]


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    ####################################################
    #Helpers
    ####################################################

    def_infer_xml_builder_from_tree(self,tree):
        self.ensure_one()
        ubl_version=tree.find('{*}UBLVersionID')
        customization_id=tree.find('{*}CustomizationID')
        iftree.tag=='{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice':
            returnself.env['account.edi.xml.cii']
        ifubl_versionisnotNone:
            ifubl_version.text=='2.0':
                returnself.env['account.edi.xml.ubl_20']
            ifubl_version.textin('2.1','2.2','2.3'):
                returnself.env['account.edi.xml.ubl_21']
        ifcustomization_idisnotNone:
            if'xrechnung'incustomization_id.text:
                returnself.env['account.edi.xml.ubl_de']
            ifcustomization_id.text=='urn:cen.eu:en16931:2017#compliant#urn:fdc:nen.nl:nlcius:v1.0':
                returnself.env['account.edi.xml.ubl_nl']
            #AllowtoparseanyformatderivedfromtheeuropeansemanticnormEN16931
            if'urn:cen.eu:en16931:2017'incustomization_id.text:
                returnself.env['account.edi.xml.ubl_bis3']
        return

    def_get_xml_builder(self,company):
        #seehttps://communaute.chorus-pro.gouv.fr/wp-content/uploads/2017/08/20170630_Solution-portail_Dossier_Specifications_Fournisseurs_Chorus_Facture_V.1.pdf
        #page45->ubl2.1forFranceseemsalsosupported
        ifself.code=='facturx_1_0_05':
            returnself.env['account.edi.xml.cii']
        #ifthecompany'scountryisnotintheEASmapping,nothingisgenerated
        ifself.code=='ubl_bis3'andcompany.country_id.codeinCOUNTRY_EAS:
            returnself.env['account.edi.xml.ubl_bis3']
        #theEDIoptionwillonlyappearonthejournalofgermancompanies
        ifself.code=='ubl_de'andcompany.country_id.code=='DE':
            returnself.env['account.edi.xml.ubl_de']
        #theEDIoptionwillonlyappearonthejournalofbelgiancompanies
        ifself.code=='efff_1'andcompany.country_id.code=='BE':
            returnself.env['account.edi.xml.ubl_efff']

    def_is_ubl_cii_available(self,company):
        """
        Returnsabooleanindicatingwhetheritispossibletogenerateanxmlfileusingoneoftheformatsfromthis
        moduleornot
        """
        returnself._get_xml_builder(company)isnotNone

    ####################################################
    #Export:Account.edi.formatoverride
    ####################################################

    def_is_required_for_invoice(self,invoice):
        #EXTENDSaccount_edi
        self.ensure_one()
        ifself.codenotinFORMAT_CODES:
            returnsuper()._is_required_for_invoice(invoice)

        returnself._is_ubl_cii_available(invoice.company_id)andinvoice.move_typein('out_invoice','out_refund')

    def_is_compatible_with_journal(self,journal):
        #EXTENDSaccount_edi
        #theformatsappearonthejournalonlyiftheyarecompatible(e.g.NLCIUSonlyappearfordutchcompanies)
        self.ensure_one()
        ifself.codenotinFORMAT_CODES:
            returnsuper()._is_compatible_with_journal(journal)
        returnself._is_ubl_cii_available(journal.company_id)andjournal.type=='sale'

    def_is_enabled_by_default_on_journal(self,journal):
        #EXTENDSaccount_edi
        #onlyfacturxisenabledbydefault,theotherformatsaren't
        self.ensure_one()
        ifself.codenotinFORMAT_CODES:
            returnsuper()._is_enabled_by_default_on_journal(journal)
        returnself.code=='facturx_1_0_05'

    def_post_invoice_edi(self,invoices,test_mode=False):
        #EXTENDSaccount_edi
        self.ensure_one()

        ifself.codenotinFORMAT_CODES:
            returnsuper()._post_invoice_edi(invoices,test_mode=test_mode)

        res={}
        forinvoiceininvoices:
            builder=self._get_xml_builder(invoice.company_id)
            #Fornow,theerrorsarenotdisplayedanywhere,don'twanttoannoytheuser
            xml_content,errors=builder._export_invoice(invoice)

            #DEBUG:senddirectlytothetestplatform(theoneusedbyecosio)
            #response=self.env['account.edi.common']._check_xml_ecosio(invoice,xml_content,builder._export_invoice_ecosio_schematrons())

            attachment_create_vals={
                'name':builder._export_invoice_filename(invoice),
                'raw':xml_content,
                'mimetype':'application/xml',
            }
            #wedon'twanttheFactur-X,E-FFFandNLCIUSxmltoappearintheattachmentoftheinvoicewhenconfirmingit
            #E-FFFandNLCIUSwillappearafterthepdfisgenerated,Factur-Xwillneverappear(it'scontainedinthePDF)
            ifself.codenotin['facturx_1_0_05','efff_1','nlcius_1']:
                attachment_create_vals.update({'res_id':invoice.id,'res_model':'account.move'})

            attachment=self.env['ir.attachment'].create(attachment_create_vals)
            res[invoice]={
                'success':True,
                'attachment':attachment,
            }

        returnres

    def_is_embedding_to_invoice_pdf_needed(self):
        #EXTENDSaccount_edi
        self.ensure_one()

        ifself.code=='facturx_1_0_05':
            returnTrue
        returnsuper()._is_embedding_to_invoice_pdf_needed()

    def_prepare_invoice_report(self,pdf_writer,edi_document):
        #EXTENDSaccount_edi
        self.ensure_one()
        ifself.code!='facturx_1_0_05':
            returnsuper()._prepare_invoice_report(pdf_writer,edi_document)
        ifnotedi_document.attachment_id:
            return

        pdf_writer.embed_flectra_attachment(edi_document.attachment_id,subtype='text/xml')
        ifnotpdf_writer.is_pdfaandstr2bool(
                self.env['ir.config_parameter'].sudo().get_param('edi.use_pdfa','False')):
            try:
                pdf_writer.convert_to_pdfa()
            exceptExceptionase:
                _logger.exception("ErrorwhileconvertingtoPDF/A:%s",e)
            metadata_template=self.env.ref('account_edi_ubl_cii.account_invoice_pdfa_3_facturx_metadata',
                                             raise_if_not_found=False)
            ifmetadata_template:
                content=self.env['ir.qweb']._render('account_edi_ubl_cii.account_invoice_pdfa_3_facturx_metadata',{
                    'title':edi_document.move_id.name,
                    'date':fields.Date.context_today(self),
                })
                pdf_writer.add_file_metadata(content)

    ####################################################
    #Import:Account.edi.formatoverride
    ####################################################

    def_create_invoice_from_xml_tree(self,filename,tree,journal=None):
        #EXTENDSaccount_edi
        self.ensure_one()

        journal=journalorself.env['account.move']._get_default_journal()

        ifnotself._is_ubl_cii_available(journal.company_id):
            returnsuper()._create_invoice_from_xml_tree(filename,tree,journal=journal)

        #inferthexmlbuilder
        invoice_xml_builder=self._infer_xml_builder_from_tree(tree)

        ifinvoice_xml_builderisnotNone:
            invoice=invoice_xml_builder._import_invoice(journal,filename,tree)
            ifinvoice:
                returninvoice

        returnsuper()._create_invoice_from_xml_tree(filename,tree,journal=journal)

    def_update_invoice_from_xml_tree(self,filename,tree,invoice):
        #EXTENDSaccount_edi
        self.ensure_one()

        ifnotself._is_ubl_cii_available(invoice.company_id):
            returnsuper()._update_invoice_from_xml_tree(filename,tree,invoice)

        #inferthexmlbuilder
        invoice_xml_builder=self._infer_xml_builder_from_tree(tree)

        ifinvoice_xml_builderisnotNone:
            invoice=invoice_xml_builder._import_invoice(invoice.journal_id,filename,tree,invoice)
            ifinvoice:
                returninvoice

        returnsuper()._update_invoice_from_xml_tree(filename,tree,invoice)
