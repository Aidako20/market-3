#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportOrderedDict

fromflectraimportmodels


classProductTemplateAttributeLine(models.Model):
    _inherit='product.template.attribute.line'

    def_prepare_single_value_for_display(self):
        """Ontheproductpagegrouptogethertheattributelinesthatconcern
        thesameattributeandthathaveonlyonevalueeach.

        Indeedthoseareconsideredinformativevalues,theydonotgenerate
        choicefortheuser,sotheyaredisplayedbelowtheconfigurator.

        Thereturnedattributesareorderedastheyappearin`self`,sobased
        ontheorderoftheattributelines.
        """
        single_value_lines=self.filtered(lambdaptal:len(ptal.value_ids)==1)
        single_value_attributes=OrderedDict([(pa,self.env['product.template.attribute.line'])forpainsingle_value_lines.attribute_id])
        forptalinsingle_value_lines:
            single_value_attributes[ptal.attribute_id]|=ptal
        returnsingle_value_attributes
