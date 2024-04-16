#-*-coding:utf-8-*-


defrename_tag(cr,old_tag,new_tag):
    cr.execute(
        """UPDATEir_model_data
           SETname=%s
           WHEREmodule='l10n_de'ANDname=%s
        """,
        (new_tag,old_tag),
    )


defmigrate(cr,version):
    rename_tag(cr,"tag_de_liabilities_bs_C_1","tag_de_liabilities_bs_B_1")
    rename_tag(cr,"tag_de_liabilities_bs_C_2","tag_de_liabilities_bs_B_2")
    rename_tag(cr,"tag_de_liabilities_bs_C_3","tag_de_liabilities_bs_B_3")
    rename_tag(cr,"tag_de_liabilities_bs_D_1","tag_de_liabilities_bs_C_1")
    rename_tag(cr,"tag_de_liabilities_bs_D_2","tag_de_liabilities_bs_C_2")
    rename_tag(cr,"tag_de_liabilities_bs_D_3","tag_de_liabilities_bs_C_3")
    rename_tag(cr,"tag_de_liabilities_bs_D_4","tag_de_liabilities_bs_C_4")
    rename_tag(cr,"tag_de_liabilities_bs_D_5","tag_de_liabilities_bs_C_5")
    rename_tag(cr,"tag_de_liabilities_bs_D_6","tag_de_liabilities_bs_C_6")
    rename_tag(cr,"tag_de_liabilities_bs_D_7","tag_de_liabilities_bs_C_7")
    rename_tag(cr,"tag_de_liabilities_bs_D_8","tag_de_liabilities_bs_C_8")
    rename_tag(cr,"tag_de_liabilities_bs_E","tag_de_liabilities_bs_D")
    rename_tag(cr,"tag_de_liabilities_bs_F","tag_de_liabilities_bs_E")

    #BydeletingtagBfromir_model_dataweensurethattheORMwon'ttrytoremovethisrecord.
    #ThisisdonebecausethetagmightbealreadyusedasaFKsomewhereelse.
    cr.execute(
        """DELETEFROMir_model_data
           WHEREmodule='l10n_de'
           ANDname='tag_de_liabilities_bs_B'
        """
    )
