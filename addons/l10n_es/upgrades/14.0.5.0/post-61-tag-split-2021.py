#-*-coding:utf-8-*-

fromflectraimportapi,SUPERUSER_ID


defmigrate(cr,version):
    #Fortaxescomingfromtaxtemplates,replacegrid61bytherighttag.
    #Fortheotherones,wecan'tguesswhattouse,andtheuserwillhavetochangehis
    #configmanually,possiblycreatingatickettoasktofixhisaccountinghistory.

    defget_taxes_from_templates(templates):
        cr.execute(f"""
            SELECTarray_agg(tax.id)
            FROMaccount_taxtax
            JOINir_model_datadata
                ONdata.model='account.tax'
                ANDdata.res_id=tax.id
                ANDdata.module='l10n_es'
                ANDdata.name~'^[0-9]*_({'|'.join(templates)})\\Z'
        """)

        returncr.fetchone()[0]
    env=api.Environment(cr,SUPERUSER_ID,{})

    templates_mapping={
        'mod_303_120':['account_tax_template_s_iva_ns','account_tax_template_s_iva_ns_b'],
        'mod_303_122':['account_tax_template_s_iva_e','account_tax_template_s_iva0_isp'],
    }

    #Toruninaserveractiontofixissuesondbswithcustomtaxes,
    #replacethecontentofthisdict.
    taxes_mapping={}
    fortag_name,template_namesintemplates_mapping.items():
        taxes_from_templates=get_taxes_from_templates(template_names)
        iftaxes_from_templates:
            taxes_mapping[tag_name]=taxes_from_templates

    old_tag=env.ref('l10n_es.mod_303_61')
    fortag_name,tax_idsintaxes_mapping.items():
        #Grid61isonlyforbaserepartition.
        #Ifitwasusedfortaxesrepartition,wedon'ttouchit(andit'llrequiremanualcheck,
        #astheBOEfileprobablywon'tpassgovernmentchecks).

        new_tag=env.ref(f'l10n_es.{tag_name}')

        #Changetaxconfig
        cr.execute("""
            UPDATEaccount_account_tag_account_tax_repartition_line_reltax_rep_tag
            SETaccount_account_tag_id=%s
            FROMaccount_account_tagnew_tag,account_tax_repartition_linerepln
            WHEREtax_rep_tag.account_account_tag_id=%s
            ANDrepln.id=tax_rep_tag.account_tax_repartition_line_id
            ANDCOALESCE(repln.invoice_tax_id,repln.refund_tax_id)IN%s
        """,[new_tag.id,old_tag.id,tuple(tax_ids)])

        #Changeamlsinhistory,startingatQ32021(dateofintroductionforthenewtags)

        #Settags
        cr.execute("""
            UPDATEaccount_account_tag_account_move_line_relaml_tag
            SETaccount_account_tag_id=%s
            FROMaccount_move_lineaml,account_move_line_account_tax_relaml_tax
            WHEREaml_tag.account_move_line_id=aml.id
            ANDaml_tax.account_move_line_id=aml.id
            ANDaml.date>='2021-07-01'
            ANDaml_tax.account_tax_idIN%s
            ANDaml_tag.account_account_tag_id=%s
        """,[new_tag.id,tuple(tax_ids),old_tag.id])

        #Fixtaxauditstring
        cr.execute("""
            UPDATEaccount_move_lineaml
            SETtax_audit=REPLACE(tax_audit,%s,%s)
            FROMaccount_account_tag_account_move_line_relaml_tag
            WHEREaml_tag.account_move_line_id=aml.id
            ANDaml_tag.account_account_tag_id=%s
        """,[old_tag.name,f"{new_tag.name}:",new_tag.id])
