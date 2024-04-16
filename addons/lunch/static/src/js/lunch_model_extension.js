flectra.define("lunch/static/src/js/lunch_model_extension.js",function(require){
    "usestrict";

    constActionModel=require("web/static/src/js/views/action_model.js");

    classLunchModelExtensionextendsActionModel.Extension{

        //---------------------------------------------------------------------
        //Public
        //---------------------------------------------------------------------

        /**
         *@override
         *@returns{any}
         */
        get(property){
            switch(property){
                case"domain":returnthis.getDomain();
                case"userId":returnthis.state.userId;
            }
        }

        /**
         *@override
         */
        asyncload(){
            awaitthis._updateLocationId();
        }

        /**
         *@override
         */
        prepareState(){
            Object.assign(this.state,{
                locationId:null,
                userId:null,
            });
        }

        //---------------------------------------------------------------------
        //Actions/Getters
        //---------------------------------------------------------------------

        /**
         *@returns{Array[]|null}
         */
        getDomain(){
            if(this.state.locationId){
                return[["is_available_at","in",[this.state.locationId]]];
            }
            returnnull;
        }

        /**
         *@param{number}locationId
         *@returns{Promise}
         */
        setLocationId(locationId){
            this.state.locationId=locationId;
            this.env.services.rpc({
                route:"/lunch/user_location_set",
                params:{
                    context:this.env.session.user_context,
                    location_id:this.state.locationId,
                    user_id:this.state.userId,
                },
            });
        }

        /**
         *@param{number}userId
         *@returns{Promise}
         */
        updateUserId(userId){
            this.state.userId=userId;
            this.shouldLoad=true;
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *@returns{Promise}
         */
        async_updateLocationId(){
            this.state.locationId=awaitthis.env.services.rpc({
                route:"/lunch/user_location_get",
                params:{
                    context:this.env.session.user_context,
                    user_id:this.state.userId,
                },
            });
        }
    }

    ActionModel.registry.add("Lunch",LunchModelExtension,20);

    returnLunchModelExtension;
});
