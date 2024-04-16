fromcollectionsimportOrderedDict

importxlrd
fromflectra.toolsimportpycompat

def_is_true(s):
    returnsnotin('F','False',0,'',None,False)


classLuxTaxGenerator:

    def__init__(self,filename):
        self.workbook=xlrd.open_workbook('tax.xls')
        self.sheet_info=\
            self.workbook.sheet_by_name('INFO')
        self.sheet_taxes=\
            self.workbook.sheet_by_name('TAXES')
        self.sheet_tax_codes=\
            self.workbook.sheet_by_name('TAX.CODES')
        self.sheet_fiscal_pos_map=\
            self.workbook.sheet_by_name('FISCAL.POSITION.MAPPINGS')
        self.suffix=self.sheet_info.cell_value(4,2)

    defiter_tax_codes(self):
        keys=[c.valueforcinself.sheet_tax_codes.row(0)]
        yieldkeys
        foriinrange(1,self.sheet_tax_codes.nrows):
            row=(c.valueforcinself.sheet_tax_codes.row(i))
            d=OrderedDict(zip(keys,row))
            d['sign']=int(d['sign'])
            d['sequence']=int(d['sequence'])
            yieldd

    defiter_taxes(self):
        keys=[c.valueforcinself.sheet_taxes.row(0)]
        yieldkeys
        foriinrange(1,self.sheet_taxes.nrows):
            row=(c.valueforcinself.sheet_taxes.row(i))
            yieldOrderedDict(zip(keys,row))

    defiter_fiscal_pos_map(self):
        keys=[c.valueforcinself.sheet_fiscal_pos_map.row(0)]
        yieldkeys
        foriinrange(1,self.sheet_fiscal_pos_map.nrows):
            row=(c.valueforcinself.sheet_fiscal_pos_map.row(i))
            yieldOrderedDict(zip(keys,row))

    deftax_codes_to_csv(self):
        writer=pycompat.csv_writer(open('account.tax.code.template-%s.csv'%
                                 self.suffix,'wb'))
        tax_codes_iterator=self.iter_tax_codes()
        keys=next(tax_codes_iterator)
        writer.writerow(keys)

        #writestructuretaxcodes
        tax_codes={} #code:id
        forrowintax_codes_iterator:
            tax_code=row['code']
            iftax_codeintax_codes:
                raiseRuntimeError('duplicatetaxcode%s'%tax_code)
            tax_codes[tax_code]=row['id']
            writer.writerow([pycompat.to_text(v)forvinrow.values()])

        #readtaxesandaddleaftaxcodes
        new_tax_codes={} #id:parent_code

        defadd_new_tax_code(tax_code_id,new_name,new_parent_code):
            ifnottax_code_id:
                return
            name,parent_code=new_tax_codes.get(tax_code_id,(None,None))
            ifparent_codeandparent_code!=new_parent_code:
                raiseRuntimeError('taxcode"%s"alreadyexistwith'
                                   'parent%swhiletryingtoadditwith'
                                   'parent%s'%
                                   (tax_code_id,parent_code,new_parent_code))
            else:
                new_tax_codes[tax_code_id]=(new_name,new_parent_code)

        taxes_iterator=self.iter_taxes()
        next(taxes_iterator)
        forrowintaxes_iterator:
            ifnot_is_true(row['active']):
                continue
            ifrow['child_depend']androw['amount']!=1:
                raiseRuntimeError('amountmustbeoneifchild_depend'
                                   'for%s'%row['id'])
            #baseparent
            base_code=row['BASE_CODE']
            ifnotbase_codeorbase_code=='/':
                base_code='NA'
            ifbase_codenotintax_codes:
                raiseRuntimeError('undefinedtaxcode%s'%base_code)
            ifbase_code!='NA':
                ifrow['child_depend']:
                    raiseRuntimeError('basecodespecified'
                                       'withchild_dependfor%s'%row['id'])
            ifnotrow['child_depend']:
                #...inlux,wehavethesamecodeforinvoiceandrefund
                ifbase_code!='NA':
                    assertrow['base_code_id:id'],'missingbase_code_idfor%s'%row['id']
                assertrow['ref_base_code_id:id']==row['base_code_id:id']
                add_new_tax_code(row['base_code_id:id'],
                                 'Base-'+row['name'],
                                 base_code)
            #taxparent
            tax_code=row['TAX_CODE']
            ifnottax_codeortax_code=='/':
                tax_code='NA'
            iftax_codenotintax_codes:
                raiseRuntimeError('undefinedtaxcode%s'%tax_code)
            iftax_code=='NA':
                ifrow['amount']andnotrow['child_depend']:
                    raiseRuntimeError('TAX_CODEnotspecified'
                                       'fornon-zerotax%s'%row['id'])
                ifrow['tax_code_id:id']:
                    raiseRuntimeError('tax_code_idspecified'
                                       'fortax%s'%row['id'])
            else:
                ifrow['child_depend']:
                    raiseRuntimeError('TAX_CODEspecified'
                                       'withchild_dependfor%s'%row['id'])
                ifnotrow['amount']:
                    raiseRuntimeError('TAX_CODEspecified'
                                       'forzerotax%s'%row['id'])
                ifnotrow['tax_code_id:id']:
                    raiseRuntimeError('tax_code_idnotspecified'
                                       'fortax%s'%row['id'])
            ifnotrow['child_depend']androw['amount']:
                #...inlux,wehavethesamecodeforinvoiceandrefund
                assertrow['tax_code_id:id'],'missingtax_code_idfor%s'%row['id']
                assertrow['ref_tax_code_id:id']==row['tax_code_id:id']
                add_new_tax_code(row['tax_code_id:id'],
                                 'Taxe-'+row['name'],
                                 tax_code)

        fortax_code_idinsorted(new_tax_codes):
            name,parent_code=new_tax_codes[tax_code_id]
            writer.writerow([
                tax_code_id,
                u'lu_tct_m'+parent_code,
                tax_code_id.replace('lu_tax_code_template_',u''),
                u'1',
                u'',
                pycompat.to_text(name),
                u''
            ])

    deftaxes_to_csv(self):
        writer=pycompat.csv_writer(open('account.tax.template-%s.csv'%
                                     self.suffix,'wb'))
        taxes_iterator=self.iter_taxes()
        keys=next(taxes_iterator)
        writer.writerow(keys[3:]+['sequence'])
        seq=100
        forrowinsorted(taxes_iterator,key=lambdar:r['description']):
            ifnot_is_true(row['active']):
                continue
            seq+=1
            ifrow['parent_id:id']:
                cur_seq=seq+1000
            else:
                cur_seq=seq
            writer.writerow([
                pycompat.to_text(v)
                forvinlist(row.values())[3:]
            ]+[cur_seq])

    deffiscal_pos_map_to_csv(self):
        writer=pycompat.csv_writer(open('account.fiscal.'
                                     'position.tax.template-%s.csv'%
                                     self.suffix,'wb'))
        fiscal_pos_map_iterator=self.iter_fiscal_pos_map()
        keys=next(fiscal_pos_map_iterator)
        writer.writerow(keys)
        forrowinfiscal_pos_map_iterator:
            writer.writerow([pycompat.to_text(s)forsinrow.values()])


if__name__=='__main__':
    o=LuxTaxGenerator('tax.xls')
    o.tax_codes_to_csv()
    o.taxes_to_csv()
    o.fiscal_pos_map_to_csv()
