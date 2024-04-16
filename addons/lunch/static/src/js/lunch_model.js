flectra.define('lunch.LunchModel',function(require){
"usestrict";

/**
 *ThisfiledefinestheModelfortheLunchKanbanview,whichisan
 *overrideoftheKanbanModel.
 */

varsession=require('web.session');
varBasicModel=require('web.BasicModel');

varLunchModel=BasicModel.extend({
    init:function(){
        this.locationId=false;
        this.userId=false;
        this._promInitLocation=null;

        this._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@return{Promise}resolvedwiththelocationdomain
     */
    getLocationDomain:function(){
        varself=this;
        returnthis._initUserLocation().then(function(){
            returnself._buildLocationDomainLeaf()?[self._buildLocationDomainLeaf()]:[];
        });
    },
    __load:function(){
        varself=this;
        varargs=arguments;
        var_super=this._super;

        returnthis._initUserLocation().then(function(){
            varparams=args[0];
            self._addOrUpdate(params.domain,self._buildLocationDomainLeaf());

            return_super.apply(self,args);
        });
    },
    __reload:function(id,options){
        vardomain=options&&options.domain||this.localData[id].domain;

        this._addOrUpdate(domain,this._buildLocationDomainLeaf());
        options=_.extend(options,{domain:domain});

        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _addOrUpdate:function(domain,subDomain){
        if(subDomain&&subDomain.length){
            varkey=subDomain[0];
            varindex=_.findIndex(domain,function(val){
                returnval[0]===key;
            });

            if(index<0){
                domain.push(subDomain);
            }else{
                domain[index]=subDomain;
            }

            returndomain;
        }

        returndomain;
    },
    /**
     *Buildsthedomainleafcorrespondingtothecurrentuser'slocation
     *
     *@private
     *@return{(Array[])|undefined}
     */
    _buildLocationDomainLeaf:function(){
        if(this.locationId){
            return['is_available_at','in',[this.locationId]];
        }
    },
    _getUserLocation:function(){
        returnthis._rpc({
            route:'/lunch/user_location_get',
            params:{
                context:session.user_context,
                user_id:this.userId,
            },
        });
    },
    /**
     *Getstheuserlocationonce.
     *Canbetriggeredfromanywhere
     *Usefultoinjectthelocationdomaininthesearchpanel
     *
     *@private
     *@return{Promise}
     */
    _initUserLocation:function(){
        varself=this;
        if(!this._promInitLocation){
            this._promInitLocation=newPromise(function(resolve){
                self._getUserLocation().then(function(locationId){
                    self.locationId=locationId;
                    resolve();
                });
            });
        }
        returnthis._promInitLocation;
    },
    _updateLocation:function(locationId){
        this.locationId=locationId;
        returnPromise.resolve();
    },
    _updateUser:function(userId){
        this.userId=userId;
        this._promInitLocation=null;
        returnthis._initUserLocation();
    }
});

returnLunchModel;

});
