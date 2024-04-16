#-*-coding:utf-8-*-

defconvert_field(cr,model,field,target_model):
    table=model.replace('.','_')

    cr.execute("""SELECT1
                    FROMinformation_schema.columns
                   WHEREtable_name=%s
                     ANDcolumn_name=%s
               """,(table,field))
    ifnotcr.fetchone():
        return

    cr.execute("SELECTidFROMir_model_fieldsWHEREmodel=%sANDname=%s",(model,field))
    [fields_id]=cr.fetchone()

    cr.execute("""
        INSERTINTOir_property(name,type,fields_id,company_id,res_id,value_reference)
        SELECT%(field)s,'many2one',%(fields_id)s,company_id,CONCAT('{model},',id),
               CONCAT('{target_model},',{field})
          FROM{table}t
         WHERE{field}ISNOTNULL
           ANDNOTEXISTS(SELECT1
                            FROMir_property
                           WHEREfields_id=%(fields_id)s
                             ANDcompany_id=t.company_id
                             ANDres_id=CONCAT('{model},',t.id))
    """.format(**locals()),locals())

    cr.execute('ALTERTABLE"{0}"DROPCOLUMN"{1}"CASCADE'.format(table,field))

defmigrate(cr,version):
    convert_field(cr,'res.partner','property_purchase_currency_id','res.currency')
    convert_field(cr,'product.template',
                  'property_account_creditor_price_difference','account.account')
