#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importio
importre
importxlwt

fromflectraimportfields,models
fromflectra.tools.miscimportformat_date


COLUMN_HEADER_MAP={
    "Reporting_Month":"invoice_date",
    "Vendor_TIN":"vat",
    "branchCode":"branch_code",
    "companyName":"company_name",
    "surName":"last_name",
    "firstName":"first_name",
    "middleName":"middle_name",
    "address":"address",
    "nature":"product_name",
    "ATC":"atc",
    "income_payment":"price_subtotal",
    "ewt_rate":"amount",
    "tax_amount":"tax_amount",
}

classGenerate2307Wizard(models.TransientModel):
    _name="l10n_ph_2307.wizard"
    _description="Exports2307datatoaXLSfile."

    moves_to_export=fields.Many2many("account.move",string="JouralToInclude")
    generate_xls_file=fields.Binary(
        "Generatedfile",
        help="TechnicalfieldusedtotemporarilyholdthegeneratedXLSfilebeforeitsdownloaded."
    )

    def_write_single_row(self,worksheet,worksheet_row,values):
        forindex,fieldinenumerate(COLUMN_HEADER_MAP.values()):
            worksheet.write(worksheet_row,index,label=values[field])

    def_write_rows(self,worksheet,moves):
        worksheet_row=0
        formoveinmoves:
            worksheet_row+=1
            partner=move.partner_id
            partner_address_info=[partner.street,partner.street2,partner.city,partner.state_id.name,partner.country_id.name]
            values={
                'invoice_date':format_date(self.env,move.invoice_date,date_format="MM/dd/yyyy"),
                'vat':re.sub(r'\-','',partner.vat)[:9]ifpartner.vatelse'',
                'branch_code':partner.branch_codeor'000',
                'company_name':partner.commercial_partner_id.name,
                'first_name':partner.first_nameor'',
                'middle_name':partner.middle_nameor'',
                'last_name':partner.last_nameor'',
                'address':','.join([valforvalinpartner_address_infoifval])
            }
            forinvoice_lineinmove.invoice_line_ids.filtered(lambdal:notl.display_type):
                fortaxininvoice_line.tax_ids.filtered(lambdax:x.l10n_ph_atc):
                    values['product_name']=re.sub(r'[\(\)]','',invoice_line.product_id.name)
                    values['atc']=tax.l10n_ph_atc
                    values['price_subtotal']=invoice_line.price_subtotal
                    values['amount']=tax.amount
                    values['tax_amount']=tax._compute_amount(invoice_line.price_subtotal,invoice_line.price_unit)
                    self._write_single_row(worksheet,worksheet_row,values)
                    worksheet_row+=1

    defaction_generate(self):
        """Generateaxlsformatfileforimportingto
        https://bir-excel-uploader.com/excel-file-to-bir-dat-format/#bir-form-2307-settings.
        ThiswebsitewillthengenerateaBIR2307formatexcelfileforuploadingtothe
        PHgovernment.
        """
        self.ensure_one()

        file_data=io.BytesIO()
        workbook=xlwt.Workbook(encoding='utf-8')
        worksheet=workbook.add_sheet('Form2307')

        forindex,col_headerinenumerate(COLUMN_HEADER_MAP.keys()):
            worksheet.write(0,index,label=col_header)

        self._write_rows(worksheet,self.moves_to_export)

        workbook.save(file_data)
        file_data.seek(0)
        self.generate_xls_file=base64.b64encode(file_data.read())

        return{
            "type":"ir.actions.act_url",
            "target":"self",
            "url":"/web/content?model=l10n_ph_2307.wizard&download=true&field=generate_xls_file&filename=Form_2307.xls&id={}".format(self.id),
        }
