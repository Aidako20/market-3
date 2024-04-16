#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importitertools

fromflectraimportmodels


classProductTemplate(models.Model):
    _inherit='product.template'

    def_get_template_matrix(self,**kwargs):
        self.ensure_one()
        company_id=kwargs.get('company_id',None)orself.company_idorself.env.company
        currency_id=kwargs.get('currency_id',None)orself.currency_id
        display_extra=kwargs.get('display_extra_price',False)
        attribute_lines=self.valid_product_template_attribute_line_ids

        Attrib=self.env['product.template.attribute.value']
        first_line_attributes=attribute_lines[0].product_template_value_ids._only_active()
        attribute_ids_by_line=[line.product_template_value_ids._only_active().idsforlineinattribute_lines]

        header=[{"name":self.display_name}]+[
            attr._grid_header_cell(
                fro_currency=self.currency_id,
                to_currency=currency_id,
                company=company_id,
                display_extra=display_extra
            )forattrinfirst_line_attributes]

        result=[[]]
        forpoolinattribute_ids_by_line:
            result=[x+[y]foryinpoolforxinresult]
        args=[iter(result)]*len(first_line_attributes)
        rows=itertools.zip_longest(*args)

        matrix=[]
        forrowinrows:
            row_attributes=Attrib.browse(row[0][1:])
            row_header_cell=row_attributes._grid_header_cell(
                fro_currency=self.currency_id,
                to_currency=currency_id,
                company=company_id,
                display_extra=display_extra)
            result=[row_header_cell]

            forcellinrow:
                combination=Attrib.browse(cell)
                is_possible_combination=self._is_combination_possible(combination)
                cell.sort()
                result.append({
                    "ptav_ids":cell,
                    "qty":0,
                    "is_possible_combination":is_possible_combination
                })
            matrix.append(result)

        return{
            "header":header,
            "matrix":matrix,
        }


classProductTemplateAttributeValue(models.Model):
    _inherit="product.template.attribute.value"

    def_grid_header_cell(self,fro_currency,to_currency,company,display_extra=True):
        """Generateaheadermatrixcellfor1ormultipleattributes.

        :paramres.currencyfro_currency:
        :paramres.currencyto_currency:
        :paramres.companycompany:
        :parambooldisplay_extra:whetherextrapricesshouldbedisplayedinthecell
            Truebydefault,usedtoavoidshowingextrapricesonpurchases.
        :returns:cellwithname(andpriceifanyprice_extraisdefinedonself)
        :rtype:dict
        """
        header_cell={
            'name':'•'.join([attr.nameforattrinself])ifselfelse""
        } #The""istoavoidhaving'Notavailable'ifthetemplatehasonlyoneattributeline.
        extra_price=sum(self.mapped('price_extra'))ifdisplay_extraelse0
        ifextra_price:
            sign='+'ifextra_price>0else'-'
            header_cell.update({
                "price":sign+self.env['ir.qweb.field.monetary'].value_to_html(
                    extra_price,{
                        'from_currency':fro_currency,
                        'display_currency':to_currency,
                        'company_id':company.id,
                        }
                    )
            })
        returnheader_cell
