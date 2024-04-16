#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importre
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.toolsimportfloat_round

FK_HEAD_LIST=['FK','KD_JENIS_TRANSAKSI','FG_PENGGANTI','NOMOR_FAKTUR','MASA_PAJAK','TAHUN_PAJAK','TANGGAL_FAKTUR','NPWP','NAMA','ALAMAT_LENGKAP','JUMLAH_DPP','JUMLAH_PPN','JUMLAH_PPNBM','ID_KETERANGAN_TAMBAHAN','FG_UANG_MUKA','UANG_MUKA_DPP','UANG_MUKA_PPN','UANG_MUKA_PPNBM','REFERENSI','KODE_DOKUMEN_PENDUKUNG']

LT_HEAD_LIST=['LT','NPWP','NAMA','JALAN','BLOK','NOMOR','RT','RW','KECAMATAN','KELURAHAN','KABUPATEN','PROPINSI','KODE_POS','NOMOR_TELEPON']

OF_HEAD_LIST=['OF','KODE_OBJEK','NAMA','HARGA_SATUAN','JUMLAH_BARANG','HARGA_TOTAL','DISKON','DPP','PPN','TARIF_PPNBM','PPNBM']


def_csv_row(data,delimiter=',',quote='"'):
    returnquote+(quote+delimiter+quote).join([str(x).replace(quote,'\\'+quote)forxindata])+quote+'\n'


classAccountMove(models.Model):
    _inherit="account.move"

    l10n_id_tax_number=fields.Char(string="TaxNumber",copy=False)
    l10n_id_replace_invoice_id=fields.Many2one('account.move',string="ReplaceInvoice", domain="['|','&','&',('state','=','posted'),('partner_id','=',partner_id),('reversal_move_id','!=',False),('state','=','cancel')]",copy=False)
    l10n_id_attachment_id=fields.Many2one('ir.attachment',readonly=True,copy=False)
    l10n_id_csv_created=fields.Boolean('CSVCreated',compute='_compute_csv_created',copy=False)
    l10n_id_kode_transaksi=fields.Selection([
            ('01','01KepadaPihakyangBukanPemungutPPN(CustomerBiasa)'),
            ('02','02KepadaPemungutBendaharawan(DinasKepemerintahan)'),
            ('03','03KepadaPemungutSelainBendaharawan(BUMN)'),
            ('04','04DPPNilaiLain(PPN1%)'),
            ('05','05BesaranTertentu'),
            ('06','06PenyerahanLainnya(TurisAsing)'),
            ('07','07PenyerahanyangPPN-nyaTidakDipungut(KawasanEkonomiKhusus/Batam)'),
            ('08','08PenyerahanyangPPN-nyaDibebaskan(ImporBarangTertentu)'),
            ('09','09PenyerahanAktiva(Pasal16DUUPPN)'),
        ],string='KodeTransaksi',help='Duadigitpertamanomorpajak',
        readonly=False,states={'posted':[('readonly',True)],'cancel':[('readonly',True)]},copy=False,
        compute="_compute_kode_transaksi",store=True)
    l10n_id_need_kode_transaksi=fields.Boolean(compute='_compute_need_kode_transaksi')

    @api.onchange('l10n_id_tax_number')
    def_onchange_l10n_id_tax_number(self):
        forrecordinself:
            ifrecord.l10n_id_tax_numberandrecord.move_typenotinself.get_purchase_types():
                raiseUserError(_("YoucanonlychangethenumbermanuallyforaVendorBillsandCreditNotes"))

    @api.depends('l10n_id_attachment_id')
    def_compute_csv_created(self):
        forrecordinself:
            record.l10n_id_csv_created=bool(record.l10n_id_attachment_id)

    @api.depends('partner_id')
    def_compute_kode_transaksi(self):
        formoveinself:
            move.l10n_id_kode_transaksi=move.partner_id.l10n_id_kode_transaksi

    @api.depends('partner_id')
    def_compute_need_kode_transaksi(self):
        formoveinself:
            move.l10n_id_need_kode_transaksi=move.partner_id.l10n_id_pkpandnotmove.l10n_id_tax_numberandmove.move_type=='out_invoice'andmove.country_code=='ID'

    @api.constrains('l10n_id_kode_transaksi','line_ids')
    def_constraint_kode_ppn(self):
        ppn_tag=self.env.ref('l10n_id.ppn_tag')
        formoveinself.filtered(lambdam:m.l10n_id_kode_transaksi!='08'):
            ifany(ppn_tag.idinline.tax_tag_ids.idsforlineinmove.line_idsifline.exclude_from_invoice_tabisFalseandnotline.display_type)\
                    andany(ppn_tag.idnotinline.tax_tag_ids.idsforlineinmove.line_idsifline.exclude_from_invoice_tabisFalseandnotline.display_type):
                raiseUserError(_('CannotmixVATsubjectandNon-VATsubjectitemsinthesameinvoicewiththiskodetransaksi.'))
        formoveinself.filtered(lambdam:m.l10n_id_kode_transaksi=='08'):
            ifany(ppn_tag.idinline.tax_tag_ids.idsforlineinmove.line_idsifline.exclude_from_invoice_tabisFalseandnotline.display_type):
                raiseUserError('Kodetransaksi08isonlyfornonVATsubjectitems.')

    @api.constrains('l10n_id_tax_number')
    def_constrains_l10n_id_tax_number(self):
        forrecordinself.filtered('l10n_id_tax_number'):
            ifrecord.l10n_id_tax_number!=re.sub(r'\D','',record.l10n_id_tax_number):
                record.l10n_id_tax_number=re.sub(r'\D','',record.l10n_id_tax_number)
            iflen(record.l10n_id_tax_number)!=16:
                raiseUserError(_('Ataxnumbershouldhave16digits'))
            elifrecord.l10n_id_tax_number[:2]notindict(self._fields['l10n_id_kode_transaksi'].selection).keys():
                raiseUserError(_('AtaxnumbermustbeginbyavalidKodeTransaksi'))
            elifrecord.l10n_id_tax_number[2]notin('0','1'):
                raiseUserError(_('Thethirddigitofataxnumbermustbe0or1'))

    def_post(self,soft=True):
        """SetE-Fakturnumberaftervalidation."""
        formoveinself:
            ifmove.l10n_id_need_kode_transaksi:
                ifnotmove.l10n_id_kode_transaksi:
                    raiseValidationError(_('YouneedtoputaKodeTransaksiforthispartner.'))
                ifmove.l10n_id_replace_invoice_id.l10n_id_tax_number:
                    ifnotmove.l10n_id_replace_invoice_id.l10n_id_attachment_id:
                        raiseValidationError(_('Replacementinvoiceonlyforinvoicesonwhichthee-Fakturisgenerated.'))
                    rep_efaktur_str=move.l10n_id_replace_invoice_id.l10n_id_tax_number
                    move.l10n_id_tax_number='%s1%s'%(move.l10n_id_kode_transaksi,rep_efaktur_str[3:])
                else:
                    efaktur=self.env['l10n_id_efaktur.efaktur.range'].pop_number(move.company_id.id)
                    ifnotefaktur:
                        raiseValidationError(_('ThereisnoEfakturnumberavailable. Pleaseconfiguretherangeyougetfromthegovernmentinthee-Fakturmenu.'))
                    move.l10n_id_tax_number='%s0%013d'%(str(move.l10n_id_kode_transaksi),efaktur)
        returnsuper()._post(soft)

    defreset_efaktur(self):
        """ResetE-Faktur,soitcanbeuseforotherinvoice."""
        formoveinself:
            ifmove.l10n_id_attachment_id:
                raiseUserError(_('Youhavealreadygeneratedthetaxreportforthisdocument:%s',move.name))
            self.env['l10n_id_efaktur.efaktur.range'].push_number(move.company_id.id,move.l10n_id_tax_number[3:])
            move.message_post(
                body='e-FakturReset:%s'%(move.l10n_id_tax_number),
                subject="ResetEfaktur")
            move.l10n_id_tax_number=False
        returnTrue

    defdownload_csv(self):
        action={
            'type':'ir.actions.act_url',
            'url':"web/content/?model=ir.attachment&id="+str(self.l10n_id_attachment_id.id)+"&filename_field=name&field=datas&download=true&name="+self.l10n_id_attachment_id.name,
            'target':'self'
        }
        returnaction

    defdownload_efaktur(self):
        """Collectthedataandexecutefunction_generate_efaktur."""
        forrecordinself:
            ifrecord.state=='draft':
                raiseValidationError(_('CouldnotdownloadE-fakturindraftstate'))

            ifrecord.partner_id.l10n_id_pkpandnotrecord.l10n_id_tax_number:
                raiseValidationError(_('Connect%(move_number)swithE-fakturtodownloadthisreport',move_number=record.name))

        self._generate_efaktur(',')
        returnself.download_csv()

    def_generate_efaktur_invoice(self,delimiter):
        """GenerateE-Fakturforcustomerinvoice."""
        #InvoiceofCustomer
        company_id=self.company_id
        dp_product_id=self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')

        output_head='%s%s%s'%(
            _csv_row(FK_HEAD_LIST,delimiter),
            _csv_row(LT_HEAD_LIST,delimiter),
            _csv_row(OF_HEAD_LIST,delimiter),
        )

        formoveinself.filtered(lambdam:m.state=='posted'):
            eTax=move._prepare_etax()

            nik=str(move.partner_id.l10n_id_nik)ifnotmove.partner_id.vatelse''

            ifmove.l10n_id_replace_invoice_id:
                number_ref=str(move.l10n_id_replace_invoice_id.name)+"replacedby"+str(move.name)+""+nik
            else:
                number_ref=str(move.name)+""+nik

            street=','.join([xforxin(move.partner_id.street,move.partner_id.street2)ifx])

            invoice_npwp='000000000000000'
            ifmove.partner_id.vatandlen(move.partner_id.vat)>=12:
                invoice_npwp=move.partner_id.vat
            elif(notmove.partner_id.vatorlen(move.partner_id.vat)<12)andmove.partner_id.l10n_id_nik:
                invoice_npwp=move.partner_id.l10n_id_nik
            invoice_npwp=invoice_npwp.replace('.','').replace('-','')

            #HereallfieldsorcolumnsbasedoneTaxInvoiceThirdParty
            eTax['KD_JENIS_TRANSAKSI']=move.l10n_id_tax_number[0:2]or0
            eTax['FG_PENGGANTI']=move.l10n_id_tax_number[2:3]or0
            eTax['NOMOR_FAKTUR']=move.l10n_id_tax_number[3:]or0
            eTax['MASA_PAJAK']=move.invoice_date.month
            eTax['TAHUN_PAJAK']=move.invoice_date.year
            eTax['TANGGAL_FAKTUR']='{0}/{1}/{2}'.format(move.invoice_date.day,move.invoice_date.month,move.invoice_date.year)
            eTax['NPWP']=invoice_npwp
            eTax['NAMA']=move.partner_id.nameifeTax['NPWP']=='000000000000000'elsemove.partner_id.l10n_id_tax_nameormove.partner_id.name
            eTax['ALAMAT_LENGKAP']=move.partner_id.contact_address.replace('\n','')ifeTax['NPWP']=='000000000000000'elsemove.partner_id.l10n_id_tax_addressorstreet
            eTax['JUMLAH_DPP']=int(float_round(move.amount_untaxed,0))#currencyroundedtotheunit
            eTax['JUMLAH_PPN']=int(float_round(move.amount_tax,0))
            eTax['ID_KETERANGAN_TAMBAHAN']='1'ifmove.l10n_id_kode_transaksi=='07'else''
            eTax['REFERENSI']=number_ref
            eTax['KODE_DOKUMEN_PENDUKUNG']='0'

            lines=move.line_ids.filtered(lambdax:x.product_id.id==int(dp_product_id)andx.price_unit<0andnotx.display_type)
            eTax['FG_UANG_MUKA']=0
            eTax['UANG_MUKA_DPP']=int(abs(sum(lines.mapped(lambdal:float_round(l.price_subtotal,0)))))
            eTax['UANG_MUKA_PPN']=int(abs(sum(lines.mapped(lambdal:float_round(l.price_total-l.price_subtotal,0)))))

            company_npwp=company_id.partner_id.vator'000000000000000'

            fk_values_list=['FK']+[eTax[f]forfinFK_HEAD_LIST[1:]]
            eTax['JALAN']=company_id.partner_id.l10n_id_tax_addressorcompany_id.partner_id.street
            eTax['NOMOR_TELEPON']=company_id.phoneor''

            lt_values_list=['FAPR',company_npwp,company_id.name]+[eTax[f]forfinLT_HEAD_LIST[3:]]

            #HOWTOADD2lineto1lineforfreeproduct
            free,sales=[],[]

            forlineinmove.line_ids.filtered(lambdal:notl.exclude_from_invoice_tabandnotl.display_type):
                #*invoice_line_unit_priceispriceunituseforharga_satuan'scolumn
                #*invoice_line_quantityisquantityuseforjumlah_barang'scolumn
                #*invoice_line_total_priceisbrutopriceuseforharga_total'scolumn
                #*invoice_line_discount_m2misdiscountpriceusefordiskon'scolumn
                #*line.price_subtotalissubtotalpriceusefordpp'scolumn
                #*tax_lineorfree_tax_lineistaxpriceuseforppn'scolumn
                free_tax_line=tax_line=bruto_total=total_discount=0.0

                fortaxinline.tax_ids:
                    iftax.amount>0:
                        tax_line+=line.price_subtotal*(tax.amount/100.0)

                discount=1-(line.discount/100)
                #guaranteespricetobetax-excluded
                invoice_line_total_price=line.price_subtotal/discountifdiscountelse0
                invoice_line_unit_price=invoice_line_total_price/line.quantityifline.quantityelse0

                line_dict={
                    'KODE_OBJEK':line.product_id.default_codeor'',
                    'NAMA':line.product_id.nameor'',
                    'HARGA_SATUAN':int(float_round(invoice_line_unit_price,0)),
                    'JUMLAH_BARANG':line.quantity,
                    'HARGA_TOTAL':int(float_round(invoice_line_total_price,0)),
                    'DPP':int(float_round(line.price_subtotal,0)),
                    'product_id':line.product_id.id,
                }

                ifline.price_subtotal<0:
                    fortaxinline.tax_ids:
                        free_tax_line+=(line.price_subtotal*(tax.amount/100.0))*-1.0

                    line_dict.update({
                        'DISKON':int(float_round(invoice_line_total_price-line.price_subtotal,0)),
                        'PPN':int(float_round(free_tax_line,0)),
                    })
                    free.append(line_dict)
                elifline.price_subtotal!=0.0:
                    invoice_line_discount_m2m=invoice_line_total_price-line.price_subtotal

                    line_dict.update({
                        'DISKON':int(float_round(invoice_line_discount_m2m,0)),
                        'PPN':int(float_round(tax_line,0)),
                    })
                    sales.append(line_dict)

            sub_total_before_adjustment=sub_total_ppn_before_adjustment=0.0

            #Wearefindingtheproductthathasaffected
            #byfreeproducttoadjustmentthecalculation
            #ofdiscountandsubtotal.
            #-thepricetotaloffreeproductwillbe
            #includedasadiscounttorelatedofproduct.
            forsaleinsales:
                forfinfree:
                    iff['product_id']==sale['product_id']:
                        sale['DISKON']=sale['DISKON']-f['DISKON']+f['PPN']
                        sale['DPP']=sale['DPP']+f['DPP']

                        tax_line=0

                        fortaxinline.tax_ids:
                            iftax.amount>0:
                                tax_line+=sale['DPP']*(tax.amount/100.0)

                        sale['PPN']=int(float_round(tax_line,0))

                        free.remove(f)

                sub_total_before_adjustment+=sale['DPP']
                sub_total_ppn_before_adjustment+=sale['PPN']
                bruto_total+=sale['DISKON']
                total_discount+=float_round(sale['DISKON'],2)

            output_head+=_csv_row(fk_values_list,delimiter)
            output_head+=_csv_row(lt_values_list,delimiter)
            forsaleinsales:
                of_values_list=['OF']+[str(sale[f])forfinOF_HEAD_LIST[1:-2]]+['0','0']
                output_head+=_csv_row(of_values_list,delimiter)

        returnoutput_head

    def_prepare_etax(self):
        #Thesevaluesareneverset
        return{'JUMLAH_PPNBM':0,'UANG_MUKA_PPNBM':0,'BLOK':'','NOMOR':'','RT':'','RW':'','KECAMATAN':'','KELURAHAN':'','KABUPATEN':'','PROPINSI':'','KODE_POS':'','JUMLAH_BARANG':0,'TARIF_PPNBM':0,'PPNBM':0}

    def_generate_efaktur(self,delimiter):
        ifself.filtered(lambdax:notx.l10n_id_kode_transaksi):
            raiseUserError(_('Somedocumentsdon\'thaveatransactioncode'))
        ifself.filtered(lambdax:x.move_type!='out_invoice'):
            raiseUserError(_('SomedocumentsarenotCustomerInvoices'))

        output_head=self._generate_efaktur_invoice(delimiter)
        my_utf8=output_head.encode("utf-8")
        out=base64.b64encode(my_utf8)

        attachment=self.env['ir.attachment'].create({
            'datas':out,
            'name':'efaktur_%s.csv'%(fields.Datetime.to_string(fields.Datetime.now()).replace("","_")),
            'type':'binary',
        })

        forrecordinself:
            record.message_post(attachment_ids=[attachment.id])
        self.l10n_id_attachment_id=attachment.id
        return{
            'type':'ir.actions.client',
            'tag':'reload',
        }
