flectra.define('unsplash.api',function(require){
'usestrict';

varClass=require('web.Class');
varrpc=require('web.rpc');
varMixins=require('web.mixins');
varServicesMixin=require('web.ServicesMixin');

varUnsplashCore=Class.extend(Mixins.EventDispatcherMixin,ServicesMixin,{
    /**
     *@constructor
     */
    init:function(parent){
        Mixins.EventDispatcherMixin.init.call(this,arguments);
        this.setParent(parent);

        this._cache={};
        this.clientId=false;
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Getsunsplashimagesfromquerystring.
     *
     *@param{String}querysearchterms
     *@param{Integer}pageSizenumberofimagetodisplayperpage
     *@returns{Promise}
     */
    getImages:function(query,pageSize){
        varfrom=0;
        varto=pageSize;
        varcachedData=this._cache[query];

        if(cachedData&&(cachedData.images.length>=to||(cachedData.totalImages!==0&&cachedData.totalImages<to))){
            returnPromise.resolve({images:cachedData.images.slice(from,to),isMaxed:to>cachedData.totalImages});
        }
        returnthis._fetchImages(query).then(function(cachedData){
            return{images:cachedData.images.slice(from,to),isMaxed:to>cachedData.totalImages};
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Fetchesimagesfromunsplashandstoresitincache
     *
     *@param{String}querysearchterms
     *@returns{Promise}
     *@private
     */
    _fetchImages:function(query){
        if(!this._cache[query]){
            this._cache[query]={
                images:[],
                maxPages:0,
                totalImages:0,
                pageCached:0
            };
        }
        varcachedData=this._cache[query];
        varpayload={
            query:query,
            page:cachedData.pageCached+1,
            per_page:30,//maxsizefromunsplashAPI
        };
        returnthis._rpc({
            route:'/web_unsplash/fetch_images',
            params:payload,
        }).then(function(result){
            if(result.error){
                returnPromise.reject(result.error);
            }
            cachedData.pageCached++;
            cachedData.images.push.apply(cachedData.images,result.results);
            cachedData.maxPages=result.total_pages;
            cachedData.totalImages=result.total;
            returncachedData;
        });
    },
});

returnUnsplashCore;

});
