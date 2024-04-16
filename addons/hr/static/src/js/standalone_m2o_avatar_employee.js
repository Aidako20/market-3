flectra.define('hr.StandaloneM2OAvatarEmployee',function(require){
    'usestrict';

    constStandaloneFieldManagerMixin=require('web.StandaloneFieldManagerMixin');
    constWidget=require('web.Widget');

    const{Many2OneAvatarEmployee}=require('hr.Many2OneAvatarEmployee');

    constStandaloneM2OAvatarEmployee=Widget.extend(StandaloneFieldManagerMixin,{
        className:'o_standalone_avatar_employee',

        /**
         *@override
         */
        init(parent,value){
            this._super(...arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.value=value;
        },
        /**
         *@override
         */
        willStart(){
            returnPromise.all([this._super(...arguments),this._makeAvatarWidget()]);
        },
        /**
         *@override
         */
        start(){
            this.avatarWidget.$el.appendTo(this.$el);
            returnthis._super(...arguments);
        },

        //--------------------------------------------------------------------------
        //Private
        //--------------------------------------------------------------------------

        /**
         *Createarecord,andinitializeandstarttheavatarwidget.
         *
         *@private
         *@returns{Promise}
         */
        async_makeAvatarWidget(){
            constmodelName='hr.employee';
            constfieldName='employee_id';
            constrecordId=awaitthis.model.makeRecord(modelName,[{
                name:fieldName,
                relation:modelName,
                type:'many2one',
                value:this.value,
            }]);
            conststate=this.model.get(recordId);
            this.avatarWidget=newMany2OneAvatarEmployee(this,fieldName,state);
            this._registerWidget(recordId,fieldName,this.avatarWidget);
            returnthis.avatarWidget.appendTo(document.createDocumentFragment());
        },
    });

    returnStandaloneM2OAvatarEmployee;
});
