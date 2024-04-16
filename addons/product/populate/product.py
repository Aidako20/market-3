#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging

fromflectraimportmodels
fromflectra.toolsimportpopulate

_logger=logging.getLogger(__name__)


classProductCategory(models.Model):
    _inherit="product.category"
    _populate_sizes={"small":50,"medium":500,"large":30000}

    def_populate_factories(self):
        defget_name(values=None,counter=0,complete=False,**kwargs):
            return"%s_%s_%s"%("product_category",int(complete),counter)

        #quidofparent_id???

        return[("name",populate.compute(get_name))]


classProductProduct(models.Model):
    _inherit="product.product"
    _populate_sizes={"small":150,"medium":5000,"large":60000}

    def_populate_factories(self):

        return[
            ("name",populate.constant('product_template_name_{counter}')),
            ("sequence",populate.randomize([False]+[iforiinrange(1,101)])),
            ("description",populate.constant('product_template_description_{counter}')),
            ("default_code",populate.constant('product_default_code_{counter}')),
            ("active",populate.randomize([True,False],[0.8,0.2])),
        ]
