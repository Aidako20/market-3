flectra.define('pos_cache.pos_cache',function(require){
"usestrict";

varmodels=require('point_of_sale.models');
varcore=require('web.core');
varrpc=require('web.rpc');
var_t=core._t;

varposmodel_super=models.PosModel.prototype;
models.PosModel=models.PosModel.extend({
    load_server_data:function(){
        varself=this;

        varproduct_index=_.findIndex(this.models,function(model){
            returnmodel.model==="product.product";
        });

        varproduct_model=self.models[product_index];

        //Wedon'twanttoloadproduct.productthenormal
        //uncachedway,sogetridofit.
        if(product_index!==-1){
            this.models.splice(product_index,1);
            this.product_model=product_model;
        }
        returnposmodel_super.load_server_data.apply(this,arguments).then(function(){
          //Afterloadingtheserverdatawehavetoaddtheproductmodelasitisneeded
          self.models.push(self.product_model)

          //Giveboththefieldsanddomaintopos_cacheinthe
          //backend.Thiswaywedon'thavetohardcodethese
          //valuesinthebackendandtheyautomaticallystayin
          //syncwithwhateverisdefined(andmaybeextendedby
          //othermodules)injs.
          varproduct_fields= typeofself.product_model.fields==='function' ?self.product_model.fields(self) :self.product_model.fields;
          varproduct_domain= typeofself.product_model.domain==='function' ?self.product_model.domain(self) :self.product_model.domain;
            varlimit_products_per_request=self.config.limit_products_per_request;
            varcur_request=0;
            functionnext(resolve,reject){
                vardomain=product_domain;
                if(limit_products_per_request){
                    domain=domain.slice();
                    //implementoffset-limitviaid,because"pos.cache"
                    //doesn'thavesuchfieldsandwecanaddtheminmaster
                    //branchonly
                    domain.unshift(['id','>',cur_request*limit_products_per_request],
                                   ['id','<=',(cur_request+1)*limit_products_per_request]);
                }
                returnrpc.query({
                    model:'pos.config',
                    method:'get_products_from_cache',
                    args:[self.pos_session.config_id[0],product_fields,domain],
                }).then(function(products){
                    self.db.add_products(_.map(products,function(product){
                        product.categ=_.findWhere(self.product_categories,{'id':product.categ_id[0]});
                        product.pos=self;
                        returnnewmodels.Product({},product);
                    }));
                    if(limit_products_per_request){
                        cur_request++;
                        //checkthatwehavemoreproducts
                        domain=product_domain.slice();
                        domain.unshift(['id','>',cur_request*limit_products_per_request]);
                        rpc.query({
                            model:'product.product',
                            method:'search_read',
                            args:[domain,['id']],
                            kwargs:{
                                limit:1,
                            }
                        }).then(function(products){
                            if(products.length){
                                next(resolve,reject);
                            }else{
                                resolve();
                            }
                        });
                    }else{
                        resolve();
                    }
                });
            }
            self.setLoadingMessage(_t('Loading')+'product.product',1);

            returnnewPromise((resolve,reject)=>{
                next(resolve,reject);
            });
        });
    },
});

});
